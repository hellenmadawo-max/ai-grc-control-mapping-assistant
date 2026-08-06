"""
AI Control Mapping Engine
=========================
Given free text (a security requirement, a policy excerpt, a procedure,
or a vendor questionnaire response), recommend the controls across all
five frameworks that the text most likely satisfies.

Design decision: a transparent, auditable keyword/overlap scoring model
is used as the default engine (`score_controls`). This matters for a GRC
tool -- auditors and examiners need to be able to see *why* a mapping was
suggested, not just trust a black box. `enrich_with_llm()` then optionally
calls the Anthropic API to add a plain-language rationale and flag
requirements the rule-based pass may have missed. If no API key is
configured, the tool still fully functions on the rule-based engine alone.
"""
import os
import re
from collections import defaultdict

from database.db import get_all_controls

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "for", "is", "are", "be",
    "must", "all", "with", "on", "in", "that", "this", "as", "by", "at",
    "will", "shall", "should", "any", "such",
}


def _tokenize(text: str):
    words = re.findall(r"[a-z0-9\-]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]


def score_controls(input_text: str, top_n: int = 8):
    """
    Rule-based mapping: score each control by keyword/phrase overlap between
    the control's `keywords` field (+title) and the submitted text.

    Confidence score = weighted overlap ratio, scaled 0-100. This is a
    transparent stand-in for an embedding-similarity or fine-tuned
    classifier approach that a production system would swap in.
    """
    controls = get_all_controls()
    input_tokens = set(_tokenize(input_text))
    input_lower = input_text.lower()

    scored = []
    for c in controls:
        control_keywords = [k.strip() for k in (c["keywords"] or "").split(",") if k.strip()]
        if not control_keywords:
            continue

        # Phrase-level matches (multi-word keywords like "multi-factor authentication")
        # count more heavily than single-token overlaps.
        phrase_hits = sum(1 for kw in control_keywords if kw in input_lower)
        token_hits = sum(1 for kw in control_keywords for t in _tokenize(kw) if t in input_tokens)

        if phrase_hits == 0 and token_hits == 0:
            continue

        raw_score = (phrase_hits * 3) + token_hits
        max_possible = len(control_keywords) * 3
        confidence = min(100, round((raw_score / max_possible) * 100 + (phrase_hits * 8), 1))
        confidence = min(confidence, 99.0)

        scored.append({
            "control_uid": c["control_uid"],
            "framework": c["framework"],
            "control_id": c["control_id"],
            "title": c["title"],
            "category": c["category"],
            "confidence": confidence,
            "matched_keywords": [kw for kw in control_keywords if kw in input_lower],
        })

    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:top_n]


def group_by_framework(scored_controls):
    grouped = defaultdict(list)
    for c in scored_controls:
        grouped[c["framework"]].append(c)
    return dict(grouped)


def identify_missing_requirements(input_text: str, scored_controls: list):
    """
    Lightweight heuristic gap flagging: look for common control themes
    mentioned in security requirements text that did NOT surface a strong
    match (confidence >= 50), so the analyst knows what to double check.
    """
    theme_hints = {
        "encryption": "Encryption / data protection controls",
        "backup": "Business continuity / disaster recovery controls",
        "training": "Security awareness training controls",
        "vendor": "Third-party / vendor risk controls",
        "logging": "Logging & monitoring controls",
        "patch": "Vulnerability / patch management controls",
        "incident": "Incident response controls",
    }
    matched_titles = " ".join(c["title"].lower() for c in scored_controls if c["confidence"] >= 50)
    missing = []
    for hint, label in theme_hints.items():
        if hint in input_text.lower() and hint not in matched_titles:
            missing.append(label)
    return missing


def call_claude_for_rationale(input_text: str, scored_controls: list):
    """
    Optional enrichment step: if ANTHROPIC_API_KEY is set in the environment,
    call the Anthropic API to generate a short plain-language rationale
    connecting the submitted text to the top-scored controls, and to surface
    anything the keyword engine may have missed. Fails gracefully (returns
    None) if no key is configured or the call errors -- the rule-based
    output above is already a complete result on its own.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        control_summary = "\n".join(
            f"- {c['framework']} {c['control_id']}: {c['title']} (confidence {c['confidence']}%)"
            for c in scored_controls[:5]
        )
        prompt = (
            "You are a GRC control-mapping assistant. A rule-based engine matched the "
            "following requirement text to these candidate controls:\n\n"
            f"Requirement text:\n\"{input_text}\"\n\nCandidate controls:\n{control_summary}\n\n"
            "In 3-4 sentences: (1) confirm or challenge whether these are the right controls, "
            "and (2) note any control domain the requirement implies that isn't in the list. "
            "Be concise and specific, GRC-analyst tone."
        )
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text_blocks = [b.text for b in response.content if b.type == "text"]
        return "\n".join(text_blocks)
    except Exception as e:
        return f"(LLM enrichment unavailable: {e})"
