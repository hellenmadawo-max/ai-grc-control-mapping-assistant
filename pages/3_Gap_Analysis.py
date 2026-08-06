import streamlit as st
from database.db import get_all_controls, save_gap_assessment, get_gap_assessments
from engine.gap_analysis import rate_gap, build_gap_narrative, recommend_remediation, MATURITY_LABELS
from engine.risk_scoring import compute_risk_score, score_to_rating, risk_factor_breakdown

st.set_page_config(page_title="Gap Analysis", page_icon="🔍", layout="wide")
st.title("🔍 Gap Analysis Module")
st.caption("Compare a required control state against the current implementation state to derive a gap and risk rating.")

controls = get_all_controls()
control_options = {f"{c['framework']} — {c['control_id']}: {c['title']}": c for c in controls}

with st.form("gap_form"):
    selection = st.selectbox("Control", list(control_options.keys()))
    control = control_options[selection]

    requirement = st.text_input("Requirement", value="Privileged access reviews performed quarterly")
    current_state = st.text_input("Current State", value="Reviews performed annually")

    c1, c2 = st.columns(2)
    with c1:
        maturity_level = st.select_slider(
            "Control Maturity Level", options=[0, 1, 2, 3, 4],
            value=1, format_func=lambda x: f"{x} — {MATURITY_LABELS[x]}"
        )
        has_evidence = st.checkbox("Evidence is available and current", value=False)
    with c2:
        business_impact = st.select_slider("Business Impact", ["Low", "Medium", "High", "Critical"], value="High")
        data_sensitivity = st.select_slider("Data Sensitivity", ["Low", "Medium", "High", "Critical"], value="High")
        regulatory_weight = st.select_slider("Regulatory Requirement Weight", ["Low", "Medium", "High", "Critical"], value="High")

    submitted = st.form_submit_button("Run Gap & Risk Analysis", type="primary")

if submitted:
    gap_rating = rate_gap(maturity_level, has_evidence)
    risk_score = compute_risk_score(maturity_level, has_evidence, business_impact, data_sensitivity, regulatory_weight)
    risk_rating = score_to_rating(risk_score)
    narrative = build_gap_narrative(control["title"], requirement, current_state, gap_rating)
    recommendation = recommend_remediation(control["title"], gap_rating)
    breakdown = risk_factor_breakdown(maturity_level, has_evidence, business_impact, data_sensitivity, regulatory_weight)

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Gap Rating", gap_rating)
    col2.metric("Risk Rating", risk_rating)
    col3.metric("Risk Score", f"{risk_score}/100")

    st.markdown("**Gap Narrative**")
    st.write(narrative)
    st.markdown("**Recommendation**")
    st.write(recommendation)

    st.markdown("**Risk Score Breakdown**")
    st.bar_chart(breakdown)

    save_gap_assessment({
        "control_uid": control["control_uid"], "requirement": requirement, "current_state": current_state,
        "maturity_level": maturity_level, "has_evidence": int(has_evidence),
        "business_impact": business_impact, "data_sensitivity": data_sensitivity,
        "regulatory_weight": regulatory_weight, "gap_rating": gap_rating,
        "risk_rating": risk_rating, "risk_score": risk_score, "recommendation": recommendation,
    })
    st.success("Assessment saved. View aggregate results on the Risk Dashboard page.")

st.divider()
st.subheader("Recent Gap Assessments")
recent = get_gap_assessments()[:10]
if recent:
    st.dataframe(
        [{"Control": g["control_uid"], "Requirement": g["requirement"], "Gap": g["gap_rating"],
          "Risk": g["risk_rating"], "Score": g["risk_score"]} for g in recent],
        use_container_width=True, hide_index=True
    )
else:
    st.caption("No assessments recorded yet.")
