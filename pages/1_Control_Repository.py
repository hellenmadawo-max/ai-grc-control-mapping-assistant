import streamlit as st
import pandas as pd
from database.db import get_all_controls, get_related_controls, get_frameworks

st.set_page_config(page_title="Control Repository", page_icon="📚", layout="wide")
st.title("📚 Framework Control Repository")

controls = get_all_controls()
frameworks = get_frameworks()

col1, col2 = st.columns([1, 2])
with col1:
    fw_filter = st.multiselect("Filter by framework", frameworks, default=frameworks)
with col2:
    search = st.text_input("Search title, description, or keywords")

filtered = [c for c in controls if c["framework"] in fw_filter]
if search:
    s = search.lower()
    filtered = [c for c in filtered if s in c["title"].lower() or s in (c["description"] or "").lower()
                or s in (c["keywords"] or "").lower()]

st.caption(f"Showing {len(filtered)} of {len(controls)} controls")

df = pd.DataFrame([{
    "Framework": c["framework"],
    "Control ID": c["control_id"],
    "Title": c["title"],
    "Category": c["category"],
} for c in filtered])
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Control Detail")
uid_options = {f"{c['framework']} — {c['control_id']}: {c['title']}": c["control_uid"] for c in filtered}
if uid_options:
    selection = st.selectbox("Select a control to view details and cross-framework mappings", list(uid_options.keys()))
    selected_uid = uid_options[selection]
    control = next(c for c in controls if c["control_uid"] == selected_uid)

    st.markdown(f"### {control['framework']} — {control['control_id']}: {control['title']}")
    st.write(control["description"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Evidence Requirements**")
        st.write(control["evidence_requirements"])
    with c2:
        st.markdown("**Testing Procedures**")
        st.write(control["testing_procedures"])

    st.markdown("**Related Controls (cross-framework mapping)**")
    related = get_related_controls(selected_uid)
    if related:
        rel_df = pd.DataFrame([{
            "Framework": r["framework"], "Control ID": r["control_id"], "Title": r["title"]
        } for r in related])
        st.dataframe(rel_df, use_container_width=True, hide_index=True)
    else:
        st.write("No related controls found.")
else:
    st.warning("No controls match the current filter.")
