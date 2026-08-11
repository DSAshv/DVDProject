import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="3-Week Roadmap", initial_sidebar_state="expanded")

section_header("3-Week Roadmap")

st.write(
    "### Week 1\nData Exploration, Cleaning & Initial Insights\n\n### Week 2\nVisualization & Comparative Analysis\n\n### Week 3\nDashboard, Technical Report & Final Presentation"
)

st.info("The roadmap is intentionally lightweight and focused on practical milestones for a data visualization project.")
