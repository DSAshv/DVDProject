import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Analysis Plan")

section_header("Analysis Plan")

steps = [
    "Business Questions",
    "Data Understanding",
    "Data Cleaning",
    "Data Integration",
    "Exploratory Analysis",
    "Explanatory Visualization",
    "Findings",
    "Recommendations",
]
for step in steps:
    st.markdown(f"**{step}**")
    if step != steps[-1]:
        st.markdown("↓")

st.write(
    "This plan provides a structured path from problem framing through data preparation, analysis, visualization, and recommendation formulation."
)
