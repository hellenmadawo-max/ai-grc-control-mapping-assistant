"""
AI Governance Module
=====================
Assesses an AI system across the risk dimensions emphasized by:
  - NIST AI Risk Management Framework (AI RMF 1.0): Govern, Map, Measure, Manage
  - ISO/IEC 42001:2023 AI Management System: risk-based lifecycle governance

This is a structured self-assessment questionnaire -> risk rating engine,
the same pattern used for the cybersecurity gap/risk modules, applied to
AI-specific risk dimensions (privacy, security, bias/fairness,
explainability, accountability/human oversight).
"""

RISK_DIMENSIONS = [
    "privacy_risk", "security_risk", "bias_risk", "explainability_risk", "accountability_risk",
]

DIMENSION_LABELS = {
    "privacy_risk": "Privacy Risk",
    "security_risk": "Security Risk",
    "bias_risk": "Bias / Fairness Risk",
    "explainability_risk": "Explainability Risk",
    "accountability_risk": "Accountability / Human Oversight Risk",
}

LEVEL_WEIGHT = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

RECOMMENDATION_LIBRARY = {
    "privacy_risk": {
        "High": "Conduct a data protection impact assessment (DPIA) and document lawful basis / data minimization controls for training and inference data.",
        "Critical": "Halt or restrict processing until a DPIA is completed; implement data minimization, retention limits, and consent/legal-basis review immediately.",
        "Medium": "Document data flows and retention periods for training and inference data; confirm data minimization practices.",
        "Low": "Maintain current privacy documentation; review annually or upon material system change.",
    },
    "security_risk": {
        "High": "Implement adversarial robustness testing, model access controls, and monitoring for model/data poisoning and prompt injection risks.",
        "Critical": "Immediately restrict production access, implement input/output filtering, and conduct a dedicated AI red-team assessment before continued use.",
        "Medium": "Apply standard secure-SDLC controls to the model pipeline (access control, logging, dependency scanning) and periodic adversarial testing.",
        "Low": "Maintain existing security controls; include the AI system in the standard vulnerability management cadence.",
    },
    "bias_risk": {
        "High": "Perform a formal bias/fairness audit across protected classes and affected populations; document mitigation steps before broader deployment.",
        "Critical": "Suspend use in consequential decisions until a bias audit is completed and mitigations are validated by an independent reviewer.",
        "Medium": "Establish periodic fairness testing against representative evaluation datasets and document acceptable-use boundaries.",
        "Low": "Continue periodic fairness spot-checks as part of standard model monitoring.",
    },
    "explainability_risk": {
        "High": "Implement model documentation (model card) and decision-rationale mechanisms for any consequential or customer-facing outputs.",
        "Critical": "Provide human-reviewable rationale for all consequential outputs before further deployment; document model limitations explicitly.",
        "Medium": "Document model behavior boundaries and maintain a model card describing intended use and known limitations.",
        "Low": "Maintain existing model documentation; update on material model changes.",
    },
    "accountability_risk": {
        "High": "Establish a named accountable owner and a human-in-the-loop review step for high-impact decisions; log override/appeal actions.",
        "Critical": "Require human sign-off before any consequential action derived from the system; escalate ownership to a governance committee.",
        "Medium": "Confirm a clear accountable owner exists and document the human-oversight process for edge cases.",
        "Low": "Maintain current human-oversight process; review annually.",
    },
}


def compute_overall_ai_risk(dimension_ratings: dict) -> str:
    """dimension_ratings: {dimension_key: 'Low'|'Medium'|'High'|'Critical'}"""
    total = sum(LEVEL_WEIGHT.get(v, 2) for v in dimension_ratings.values())
    max_possible = len(dimension_ratings) * LEVEL_WEIGHT["Critical"]
    ratio = total / max_possible if max_possible else 0

    if ratio >= 0.75 or "Critical" in dimension_ratings.values():
        return "Critical"
    if ratio >= 0.55:
        return "High"
    if ratio >= 0.35:
        return "Medium"
    return "Low"


def generate_recommendations(dimension_ratings: dict) -> list:
    recs = []
    for dim, level in dimension_ratings.items():
        if level in ("Medium", "High", "Critical"):
            rec = RECOMMENDATION_LIBRARY.get(dim, {}).get(level)
            if rec:
                recs.append(f"[{DIMENSION_LABELS.get(dim, dim)} - {level}] {rec}")
    if not recs:
        recs.append("No elevated AI risk dimensions identified. Maintain standard monitoring cadence and reassess upon material model or use-case change.")
    return recs


def map_to_frameworks(dimension_ratings: dict) -> dict:
    """Ties each risk dimension back to the relevant NIST AI RMF function
    and ISO/IEC 42001 clause area, for audit traceability."""
    return {
        "privacy_risk": {"NIST AI RMF": "MAP 1.1, MEASURE 2.9 (Privacy)", "ISO/IEC 42001": "Clause 8 (Operational Planning), Annex A.7 (Data for AI systems)", "EU AI Act": "Article 10 (Data and Data Governance)"},
        "security_risk": {"NIST AI RMF": "MEASURE 2.7 (Security & Resilience)", "ISO/IEC 42001": "Annex A.6 (Data), Annex A.9 (Third-party/supplier)", "EU AI Act": "Article 15 (Accuracy, Robustness and Cybersecurity)"},
        "bias_risk": {"NIST AI RMF": "MEASURE 2.11 (Fairness), MANAGE 2.2", "ISO/IEC 42001": "Annex A.5 (Impact assessment)", "EU AI Act": "Article 10 (Data and Data Governance — bias examination)"},
        "explainability_risk": {"NIST AI RMF": "MEASURE 2.9 (Explainability & Interpretability)", "ISO/IEC 42001": "Clause 7.4 (Communication), Annex A.6", "EU AI Act": "Article 13 (Transparency and Provision of Information to Users)"},
        "accountability_risk": {"NIST AI RMF": "GOVERN 1.1, GOVERN 4.1 (Human oversight)", "ISO/IEC 42001": "Clause 5 (Leadership), Annex A.4 (Roles/responsibilities)", "EU AI Act": "Article 14 (Human Oversight)"},
    }
