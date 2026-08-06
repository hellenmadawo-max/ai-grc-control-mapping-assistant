"""
Report Generator
=================
Produces downloadable Markdown reports from live application data:
  - Executive Summary Report
  - Control Mapping Report
  - Risk Assessment Report

Markdown is used so reports render cleanly in the UI, download as .md,
and can be pasted into Word/Confluence/PowerPoint without extra tooling.
"""
from datetime import datetime
from collections import Counter


def executive_summary_report(controls, gap_assessments, ai_systems):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_controls = len(controls)
    frameworks = sorted(set(c["framework"] for c in controls))
    total_gaps = len(gap_assessments)
    risk_counts = Counter(g["risk_rating"] for g in gap_assessments)

    lines = [
        "# Executive Summary Report",
        f"*Generated: {now}*",
        "",
        "## Program Overview",
        f"- **Frameworks in repository:** {len(frameworks)} ({', '.join(frameworks)})",
        f"- **Total controls cataloged:** {total_controls}",
        f"- **Gap/risk assessments performed:** {total_gaps}",
        f"- **AI systems assessed (AI Governance module):** {len(ai_systems)}",
        "",
        "## Risk Posture Summary",
    ]
    if risk_counts:
        for level in ["Critical", "High", "Medium", "Low"]:
            lines.append(f"- **{level}:** {risk_counts.get(level, 0)} finding(s)")
    else:
        lines.append("- No gap assessments recorded yet.")

    lines += [
        "",
        "## Top Compliance Risks",
    ]
    top_risks = sorted(gap_assessments, key=lambda g: g.get("risk_score") or 0, reverse=True)[:5]
    if top_risks:
        for g in top_risks:
            lines.append(f"- **[{g['risk_rating']}]** {g['requirement']} — {g.get('recommendation','')}")
    else:
        lines.append("- No findings recorded yet.")

    lines += [
        "",
        "## Recommendation",
        "Prioritize remediation of Critical and High findings above, with control ownership "
        "assigned and target dates tracked to closure. Reassess AI systems flagged Critical/High "
        "before further production use.",
    ]
    return "\n".join(lines)


def control_mapping_report(mapped_controls, input_text, missing_requirements=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Control Mapping Report",
        f"*Generated: {now}*",
        "",
        "## Submitted Requirement / Policy Text",
        f"> {input_text}",
        "",
        "## Mapped Controls",
        "| Framework | Control ID | Title | Confidence |",
        "|---|---|---|---|",
    ]
    for c in mapped_controls:
        lines.append(f"| {c['framework']} | {c['control_id']} | {c['title']} | {c['confidence']}% |")

    if missing_requirements:
        lines += ["", "## Potential Gaps in Mapping Coverage"]
        for m in missing_requirements:
            lines.append(f"- {m}")

    return "\n".join(lines)


def risk_assessment_report(gap_assessments):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Risk Assessment Report",
        f"*Generated: {now}*",
        "",
        "| Control | Requirement | Gap | Risk Rating | Risk Score | Recommendation |",
        "|---|---|---|---|---|---|",
    ]
    for g in gap_assessments:
        lines.append(
            f"| {g['control_uid']} | {g['requirement']} | {g['gap_rating']} | "
            f"{g['risk_rating']} | {g['risk_score']} | {g.get('recommendation','')} |"
        )
    return "\n".join(lines)
