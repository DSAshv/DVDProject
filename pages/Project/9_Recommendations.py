import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Recommendations")

section_header("Recommendations")

for section in ["Invest", "Intervene", "Monitor", "Avoid"]:
    st.subheader(section)
    st.write(
        "Evidence → Problem → Action → Expected Impact"
    )
    st.write("This section will be populated after the dataset has been analyzed and concrete business recommendations are available.")
