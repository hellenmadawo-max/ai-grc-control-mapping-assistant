"""
Run with: pytest tests/ -v
(from the project root, so the `database` and `engine` packages resolve)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database.db import init_db
from engine.mapping_engine import score_controls, identify_missing_requirements
from engine.gap_analysis import rate_gap
from engine.risk_scoring import compute_risk_score, score_to_rating

init_db()


def test_mfa_requirement_maps_to_access_control_controls():
    text = "All privileged accounts must use MFA and access must be reviewed quarterly."
    results = score_controls(text, top_n=10)
    assert len(results) > 0
    frameworks_hit = {r["framework"] for r in results}
    # Should surface matches across multiple frameworks, not just one
    assert len(frameworks_hit) >= 3
    assert results[0]["confidence"] > 0


def test_encryption_requirement_maps_to_encryption_controls():
    text = "Customer data must be encrypted at rest and in transit using strong cryptography."
    results = score_controls(text, top_n=10)
    titles = " ".join(r["title"].lower() for r in results)
    assert "encrypt" in titles or "cryptograph" in titles


def test_irrelevant_text_returns_no_or_few_matches():
    text = "The office kitchen will be repainted next month."
    results = score_controls(text, top_n=10)
    assert len(results) <= 2  # should not force irrelevant matches


def test_missing_requirements_flagged():
    text = "We need encryption and vendor risk review but nothing about training."
    results = score_controls(text, top_n=5)
    missing = identify_missing_requirements(text, results)
    assert isinstance(missing, list)


def test_gap_rating_logic():
    assert rate_gap(0, False) == "Critical"
    assert rate_gap(4, True) == "Low"
    assert rate_gap(2, False) == "High"


def test_risk_scoring_bounds():
    score = compute_risk_score(0, False, "Critical", "Critical", "Critical")
    assert score_to_rating(score) == "Critical"
    score_low = compute_risk_score(4, True, "Low", "Low", "Low")
    assert score_to_rating(score_low) == "Low"
