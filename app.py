import streamlit as st
from utils.ui import inject_style, page_header, section_header

st.set_page_config(
    page_title="E-Commerce Visualization Portal",
    page_icon="📊",
    layout="wide",
)

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
    "This workspace portal is designed to support the full data visualization project lifecycle, from planning and data preparation through storytelling, recommendations, and technical reporting. Use the sidebar to open the Project and Team sections."
)

section_header("Start your review")
button_col, info_col = st.columns([1, 2])
if button_col.button("Explore Project"):
    st.info("Open the Project section from the sidebar to continue with the project workflow.")
if button_col.button("View Interactive Dashboard"):
    st.info("Open the Interactive Dashboard page from the sidebar to view the future dashboard layout.")

info_col.markdown(
    """
    **Portal checklist**
    - Home and project overview
    - Data, analysis plan, and preparation placeholders
    - Visualization story layout and executive summaries
    - Team tracker, roadmap, work logs, and meeting notes
    - A planned interactive dashboard for KPIs, delivery, ratings, and geography
    """
)
