import json
import streamlit as st
import pandas as pd

from engine.mapping_engine import (
    score_controls, group_by_framework, identify_missing_requirements, call_claude_for_rationale
)
from engine.report_generator import control_mapping_report
from database.db import save_assessment

st.set_page_config(page_title="AI Mapping Engine", page_icon="🤖", layout="wide")
st.title("🤖 AI Control Mapping Engine")
st.caption("Paste a security requirement, policy excerpt, procedure, or vendor questionnaire response. "
           "The engine recommends relevant controls across all five frameworks with a confidence score.")

source_type = st.radio(
    "Input type", ["requirement", "policy_upload", "procedure_upload", "vendor_questionnaire"],
    horizontal=True, format_func=lambda x: {
        "requirement": "Security Requirement", "policy_upload": "Policy Document",
        "procedure_upload": "Procedure Document", "vendor_questionnaire": "Vendor Questionnaire Response"
    }[x]
)

uploaded_file = None
if source_type != "requirement":
    uploaded_file = st.file_uploader("Upload a text file (.txt) — or paste text below", type=["txt"])

default_text = "All privileged accounts must use MFA and access must be reviewed quarterly."
input_text = st.text_area(
    "Text to analyze",
    value=(uploaded_file.read().decode("utf-8") if uploaded_file else default_text),
    height=150,
)

use_llm = st.checkbox("Also request an LLM rationale (requires ANTHROPIC_API_KEY)", value=False)

if st.button("Analyze and Map Controls", type="primary"):
    if not input_text.strip():
        st.warning("Enter some text to analyze.")
    else:
        with st.spinner("Scoring against the control repository..."):
            results = score_controls(input_text, top_n=10)
            missing = identify_missing_requirements(input_text, results)

        if not results:
            st.error("No matching controls found. Try rephrasing with more specific security terminology "
                      "(e.g. 'encryption', 'access review', 'incident response').")
        else:
            st.success(f"Found {len(results)} candidate control mappings.")
            top = results[0]
            st.metric("Top Match Confidence", f"{top['confidence']}%", help=f"{top['framework']} {top['control_id']}")

            df = pd.DataFrame([{
                "Framework": r["framework"], "Control ID": r["control_id"], "Title": r["title"],
                "Confidence": f"{r['confidence']}%", "Matched Keywords": ", ".join(r["matched_keywords"]),
            } for r in results])
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.subheader("Grouped by Framework")
            grouped = group_by_framework(results)
            cols = st.columns(len(grouped)) if grouped else []
            for col, (fw, items) in zip(cols, grouped.items()):
                with col:
                    st.markdown(f"**{fw}**")
                    for i in items:
                        st.write(f"- {i['control_id']}: {i['title']} ({i['confidence']}%)")

            if missing:
                st.warning("**Potential mapping gaps** — this text mentions topics not strongly matched above:\n\n" +
                           "\n".join(f"- {m}" for m in missing))

            if use_llm:
                with st.spinner("Requesting LLM rationale..."):
                    rationale = call_claude_for_rationale(input_text, results)
                if rationale:
                    st.subheader("LLM Rationale")
                    st.info(rationale)
                else:
                    st.caption("No ANTHROPIC_API_KEY configured — showing rule-based results only.")

            save_assessment(input_text, source_type, json.dumps(results), notes="")

            report_md = control_mapping_report(results, input_text, missing)
            st.download_button("⬇ Download Control Mapping Report (.md)", report_md,
                                file_name="control_mapping_report.md", mime="text/markdown")
