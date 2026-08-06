import streamlit as st
import pandas as pd
from collections import Counter

from database.db import get_all_controls, get_gap_assessments, get_ai_systems, get_frameworks
from engine.report_generator import executive_summary_report, risk_assessment_report

st.set_page_config(page_title="Risk Dashboard", page_icon="📊", layout="wide")
st.title("📊 Reporting Dashboard")

controls = get_all_controls()
gaps = get_gap_assessments()
ai_systems = get_ai_systems()
frameworks = get_frameworks()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Controls Assessed", len(gaps))
col2.metric("Framework Coverage", f"{len(frameworks)} frameworks")
col3.metric("Open Gaps", len(gaps))
col4.metric("AI Systems Assessed", len(ai_systems))

st.divider()

if gaps:
    risk_counts = Counter(g["risk_rating"] for g in gaps)
    st.subheader("Risk Heat Map (Findings by Rating)")
    heat_df = pd.DataFrame({
        "Rating": ["Critical", "High", "Medium", "Low"],
        "Count": [risk_counts.get(r, 0) for r in ["Critical", "High", "Medium", "Low"]],
    })
    st.bar_chart(heat_df.set_index("Rating"))

    st.subheader("Top Compliance Risks")
    top_risks = sorted(gaps, key=lambda g: g.get("risk_score") or 0, reverse=True)[:5]
    st.dataframe(
        [{"Control": g["control_uid"], "Requirement": g["requirement"], "Risk Rating": g["risk_rating"],
          "Score": g["risk_score"], "Recommendation": g["recommendation"]} for g in top_risks],
        use_container_width=True, hide_index=True
    )

    st.subheader("Remediation Progress (Illustrative)")
    st.caption("Tracks the proportion of findings rated Low (i.e. substantially remediated) vs. still open.")
    remediated = risk_counts.get("Low", 0)
    total = len(gaps)
    st.progress(remediated / total if total else 0, text=f"{remediated}/{total} findings at Low risk")
else:
    st.info("No gap assessments recorded yet. Run some analyses on the Gap Analysis page to populate this dashboard.")

st.divider()
st.subheader("Downloadable Reports")

c1, c2 = st.columns(2)
with c1:
    exec_report = executive_summary_report(controls, gaps, ai_systems)
    st.download_button("⬇ Executive Summary Report (.md)", exec_report,
                        file_name="executive_summary_report.md", mime="text/markdown")
with c2:
    if gaps:
        risk_report = risk_assessment_report(gaps)
        st.download_button("⬇ Risk Assessment Report (.md)", risk_report,
                            file_name="risk_assessment_report.md", mime="text/markdown")
    else:
        st.caption("Risk assessment report available once gap assessments exist.")
