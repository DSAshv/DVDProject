import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Visualization Story", initial_sidebar_state="expanded")

section_header("Visualization Story")

st.write(
    "The visualization story will guide stakeholders through model questions, charts, observations, and business implications in a clear narrative layout."
)

for idx in range(1, 5):
    st.markdown(f"### Story element {idx}")
    st.write("Question")
    st.write("Chart placeholder")
    st.write("Observation")
    st.write("Business implication")
    st.markdown("---")
