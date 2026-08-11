import streamlit as st
from utils.ui import inject_style, page_header, section_header

st.set_page_config(page_title="Home")

inject_style()

page_header(
    "A Visual Study of E-Commerce Orders, Delivery & Customer Satisfaction",
    "Understanding how orders, sellers, delivery performance, geography, and customer experience interact across the e-commerce journey.",
)

section_header("Project at a glance")
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
col1.metric("Project status", "In progress", "May 2026")
col2.metric("Duration", "3 weeks")
col3.metric("Team size", "5 members")
col4.metric("Dataset", "Brazilian E-Commerce Dataset")

st.write(
    "This portal is a professional Streamlit workspace for planning, documenting, and presenting the data visualization project.")

section_header("Start your review")
button_col, info_col = st.columns([1, 2])
if button_col.button("Explore Project"):
    st.info("Use the sidebar pages under Project to review progress and placeholders.")
if button_col.button("View Interactive Dashboard"):
    st.info("Open the Interactive Dashboard page to see the future KPI layout.")

info_col.markdown(
    """
    - Home and project overview
    - Data, analysis plan, and preparation placeholders
    - Visualization story layout and executive summaries
    - Team tracker, roadmap, work logs, and meeting notes
    - A planned interactive dashboard for KPIs, delivery, ratings, and geography
    """
)
