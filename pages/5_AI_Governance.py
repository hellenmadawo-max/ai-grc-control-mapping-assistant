import streamlit as st
import pandas as pd

from engine.ai_governance import (
    compute_overall_ai_risk, generate_recommendations, map_to_frameworks, DIMENSION_LABELS
)
from database.db import save_ai_system_assessment, get_ai_systems

st.set_page_config(page_title="AI Governance", page_icon="🧭", layout="wide")
st.title("🧭 AI Governance Module")
st.caption("Assess an AI system against risk dimensions drawn from the NIST AI Risk Management Framework "
           "(AI RMF 1.0) and ISO/IEC 42001 AI Management System.")

with st.form("ai_gov_form"):
    system_name = st.text_input("AI System Name", value="Customer Service Chatbot")
    description = st.text_area("Description", value="LLM-powered chatbot handling customer account inquiries.")

    st.markdown("**Risk Dimension Ratings**")
    c1, c2 = st.columns(2)
    with c1:
        privacy_risk = st.select_slider("Privacy Risk", ["Low", "Medium", "High", "Critical"], value="Medium")
        security_risk = st.select_slider("Security Risk", ["Low", "Medium", "High", "Critical"], value="High")
        bias_risk = st.select_slider("Bias / Fairness Risk", ["Low", "Medium", "High", "Critical"], value="Low")
    with c2:
        explainability_risk = st.select_slider("Explainability Risk", ["Low", "Medium", "High", "Critical"], value="Medium")
        accountability_risk = st.select_slider("Accountability / Human Oversight Risk", ["Low", "Medium", "High", "Critical"], value="Medium")

    submitted = st.form_submit_button("Run AI Governance Assessment", type="primary")

if submitted:
    ratings = {
        "privacy_risk": privacy_risk, "security_risk": security_risk, "bias_risk": bias_risk,
        "explainability_risk": explainability_risk, "accountability_risk": accountability_risk,
    }
    overall = compute_overall_ai_risk(ratings)
    recs = generate_recommendations(ratings)
    fw_map = map_to_frameworks(ratings)

    st.divider()
    st.metric("Overall AI Risk Rating", overall)

    st.subheader("Risk Dimension Summary")
    st.dataframe(
        [{"Dimension": DIMENSION_LABELS[k], "Rating": v,
          "NIST AI RMF": fw_map[k]["NIST AI RMF"], "ISO/IEC 42001": fw_map[k]["ISO/IEC 42001"],
          "EU AI Act": fw_map[k]["EU AI Act"]}
         for k, v in ratings.items()],
        use_container_width=True, hide_index=True
    )

    st.subheader("Recommendations")
    for r in recs:
        st.write(f"- {r}")

    save_ai_system_assessment({
        "system_name": system_name, "description": description,
        "privacy_risk": privacy_risk, "security_risk": security_risk, "bias_risk": bias_risk,
        "explainability_risk": explainability_risk, "accountability_risk": accountability_risk,
        "overall_risk": overall, "recommendations": " | ".join(recs),
    })
    st.success("AI system assessment saved.")

st.divider()
st.subheader("Previously Assessed AI Systems")
systems = get_ai_systems()
if systems:
    st.dataframe(
        [{"System": s["system_name"], "Overall Risk": s["overall_risk"],
          "Privacy": s["privacy_risk"], "Security": s["security_risk"], "Bias": s["bias_risk"],
          "Explainability": s["explainability_risk"], "Accountability": s["accountability_risk"]}
         for s in systems],
        use_container_width=True, hide_index=True
    )
else:
    st.caption("No AI systems assessed yet.")
