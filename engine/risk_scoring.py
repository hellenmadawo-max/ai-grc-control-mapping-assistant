"""
AI Risk Scoring Model
=====================
A simple, explainable weighted-factor model (deliberately NOT a black box --
GRC risk scores need to be defensible to auditors and risk committees).

risk_score (0-100) = weighted sum of:
  - Control maturity gap (inverse of maturity level)   weight 0.35
  - Missing evidence                                    weight 0.15
  - Business impact                                     weight 0.20
  - Data sensitivity                                     weight 0.15
  - Regulatory weight                                    weight 0.15

Each qualitative factor (Low/Medium/High/Critical) is mapped to a 0-100
sub-score, then combined. The final numeric score is bucketed into a
Critical/High/Medium/Low rating using fixed thresholds so the mapping
from score -> label is transparent and repeatable.
"""

LEVEL_SCORE = {"Low": 25, "Medium": 50, "High": 75, "Critical": 100}

WEIGHTS = {
    "maturity_gap": 0.35,
    "evidence": 0.15,
    "business_impact": 0.20,
    "data_sensitivity": 0.15,
    "regulatory_weight": 0.15,
}


def compute_risk_score(maturity_level: int, has_evidence: bool, business_impact: str,
                        data_sensitivity: str, regulatory_weight: str) -> float:
    maturity_gap_score = (4 - maturity_level) / 4 * 100  # lower maturity -> higher risk
    evidence_score = 0 if has_evidence else 100

    score = (
        maturity_gap_score * WEIGHTS["maturity_gap"]
        + evidence_score * WEIGHTS["evidence"]
        + LEVEL_SCORE.get(business_impact, 50) * WEIGHTS["business_impact"]
        + LEVEL_SCORE.get(data_sensitivity, 50) * WEIGHTS["data_sensitivity"]
        + LEVEL_SCORE.get(regulatory_weight, 50) * WEIGHTS["regulatory_weight"]
    )
    return round(score, 1)


def score_to_rating(score: float) -> str:
    if score >= 75:
        return "Critical"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def risk_factor_breakdown(maturity_level: int, has_evidence: bool, business_impact: str,
                           data_sensitivity: str, regulatory_weight: str) -> dict:
    """Returns each weighted factor's contribution, for transparency in the UI/report."""
    maturity_gap_score = (4 - maturity_level) / 4 * 100
    evidence_score = 0 if has_evidence else 100
    return {
        "Control Maturity Gap": round(maturity_gap_score * WEIGHTS["maturity_gap"], 1),
        "Evidence Availability": round(evidence_score * WEIGHTS["evidence"], 1),
        "Business Impact": round(LEVEL_SCORE.get(business_impact, 50) * WEIGHTS["business_impact"], 1),
        "Data Sensitivity": round(LEVEL_SCORE.get(data_sensitivity, 50) * WEIGHTS["data_sensitivity"], 1),
        "Regulatory Weight": round(LEVEL_SCORE.get(regulatory_weight, 50) * WEIGHTS["regulatory_weight"], 1),
    }
