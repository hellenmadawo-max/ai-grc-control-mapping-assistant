"""
Gap Analysis Module
===================
Compares a documented requirement against the organization's current
implementation state for a given control, and derives a gap rating.

Maturity model (0-4, aligned to common CMMI-style GRC maturity scales):
  0 = Not Implemented
  1 = Ad Hoc / Informal
  2 = Defined but Inconsistent
  3 = Managed and Measured
  4 = Optimized / Continuously Improved

Gap rating is driven primarily by maturity level and evidence
availability -- a control can be "in place" operationally but still
represent a compliance gap if it can't be evidenced.
"""

MATURITY_LABELS = {
    0: "Not Implemented",
    1: "Ad Hoc / Informal",
    2: "Defined but Inconsistent",
    3: "Managed and Measured",
    4: "Optimized",
}


def rate_gap(maturity_level: int, has_evidence: bool) -> str:
    if maturity_level <= 1:
        return "Critical" if not has_evidence else "High"
    if maturity_level == 2:
        return "High" if not has_evidence else "Medium"
    if maturity_level == 3:
        return "Medium" if not has_evidence else "Low"
    # maturity_level == 4
    return "Low"


def build_gap_narrative(control_title: str, requirement: str, current_state: str,
                         gap_rating: str) -> str:
    templates = {
        "Critical": (f"'{control_title}' is required ({requirement}), but the current state "
                     f"('{current_state}') indicates the control is largely absent or unverifiable. "
                     f"This represents a critical compliance and operational risk exposure."),
        "High": (f"'{control_title}' is only partially implemented relative to the requirement "
                 f"('{requirement}'). Current state: '{current_state}'. Inconsistent application "
                 f"or missing evidence creates material audit and operational risk."),
        "Medium": (f"'{control_title}' is implemented but not fully aligned with the stated "
                   f"requirement ('{requirement}'). Current state: '{current_state}'. Tightening "
                   f"cadence, evidence, or coverage would close the remaining gap."),
        "Low": (f"'{control_title}' substantially meets the requirement ('{requirement}'). "
                f"Current state: '{current_state}'. Minor optimization opportunities may remain."),
    }
    return templates.get(gap_rating, "")


def recommend_remediation(control_title: str, gap_rating: str) -> str:
    recommendations = {
        "Critical": f"Immediately implement {control_title.lower()} and establish evidence capture; escalate to control owner and risk committee.",
        "High": f"Formalize and standardize {control_title.lower()} across all in-scope systems within the current quarter; assign an accountable control owner.",
        "Medium": f"Increase review cadence and strengthen evidence retention for {control_title.lower()}; incorporate into next internal audit cycle.",
        "Low": f"Maintain current practice for {control_title.lower()}; consider automation to sustain consistency at scale.",
    }
    return recommendations.get(gap_rating, "Review control implementation against requirement.")
