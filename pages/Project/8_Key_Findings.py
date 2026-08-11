import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Key Findings", initial_sidebar_state="expanded")

section_header("Key Findings")

st.write(
    "This executive summary page will present findings in concise cards once the analysis is complete."
)

for idx in range(1, 4):
    st.markdown(
        f"""
        <div class='card'>
            <strong>Finding {idx}</strong>
            <p>Evidence: Placeholder</p>
            <p>Business Impact: Placeholder</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
