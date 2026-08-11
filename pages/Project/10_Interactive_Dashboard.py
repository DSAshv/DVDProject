import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Interactive Dashboard", initial_sidebar_state="expanded")

section_header("Interactive Dashboard")

st.write(
    "This page is reserved for the future interactive analytics dashboard. It will host KPI summaries, delivery performance metrics, product and region views, and customer satisfaction analysis once the data is fully prepared."
)

st.warning(
    "Dashboard components are temporarily paused until the data integration and visualization stage is complete."
)
