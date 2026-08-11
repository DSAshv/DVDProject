import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Exploratory Analysis", initial_sidebar_state="expanded")

section_header("Exploratory Analysis")

sections = [
    "Orders",
    "Products",
    "Sellers",
    "Customers",
    "Delivery",
    "Reviews",
]
for name in sections:
    st.subheader(name)
    st.write("Question → Visualization → Observation → Business implication")
    st.write("Placeholder content: detailed charts and observations will be added after the dataset is prepared and analyzed.")
    st.markdown("---")
