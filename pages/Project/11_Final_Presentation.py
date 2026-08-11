import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Final Presentation", initial_sidebar_state="expanded")

section_header("Final Presentation")

st.write(
    "This page is reserved for the final presentation deliverables, slide summaries, and download links."
)

st.markdown(
    """
    - Presentation slides placeholder
    - Download presentation placeholder
    - Summary of the final story and conclusions
    """
)

st.warning("Slide deck and supporting files will be added when the final presentation materials are ready.")
