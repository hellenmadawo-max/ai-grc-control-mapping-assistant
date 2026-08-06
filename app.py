"""
AI GRC Control Mapping Assistant
Main entry point (Streamlit multipage app). Run with:
    streamlit run app.py
"""
import streamlit as st
from database.db import init_db, get_all_controls, get_gap_assessments, get_ai_systems, get_frameworks

st.set_page_config(
    page_title="AI GRC Control Mapping Assistant",
    page_icon="🛡️",
    layout="wide",
)

init_db()

st.title("🛡️ AI GRC Control Mapping Assistant")
st.caption("An AI-powered platform for cybersecurity control mapping, gap analysis, risk scoring, and AI governance.")

st.markdown("""
This application simulates an enterprise GRC automation tool. Use the pages in the
left sidebar to move through the workflow:

1. **Control Repository** — browse the multi-framework control database
2. **AI Mapping Engine** — paste a requirement/policy excerpt and get recommended control mappings
3. **Gap Analysis** — compare current state to a required control and rate the gap
4. **Risk Dashboard** — view aggregate risk posture, heat map, and download reports
5. **AI Governance** — assess an AI system against NIST AI RMF / ISO 42001 risk dimensions
""")

controls = get_all_controls()
gaps = get_gap_assessments()
ai_systems = get_ai_systems()
frameworks = get_frameworks()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Frameworks Loaded", len(frameworks))
col2.metric("Controls Cataloged", len(controls))
col3.metric("Gap/Risk Assessments", len(gaps))
col4.metric("AI Systems Assessed", len(ai_systems))

st.subheader("Frameworks in the Repository")
st.write(", ".join(frameworks))

st.info(
    "💡 **About the AI mapping engine:** by default this app uses a transparent, "
    "auditable keyword/overlap scoring model so every recommendation is explainable. "
    "If you set an `ANTHROPIC_API_KEY` environment variable, the AI Mapping Engine page "
    "will also call the Claude API to add a plain-language rationale on top of the "
    "rule-based result."
)
