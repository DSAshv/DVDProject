import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Interactive Dashboard", initial_sidebar_state="expanded")

section_header("Interactive Dashboard")

st.write(
    "This page is designed to house the consolidated KPI view and interactive charts for orders, delivery, product categories, seller risk, regions, and customer ratings."
)

st.markdown(
    """
    - KPI overview
    - Orders and sales
    - Delivery performance
    - Product category performance
    - Seller performance and risk
    - Region and satisfaction heatmaps
    - Customer rating distribution
    """
)

st.info("Interactive dashboard components will be added after the data integration and analysis steps are complete.")
