import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Work Logs", initial_sidebar_state="expanded")

section_header("Work Logs")

logs = [
    {"Date": "2026-05-01", "Member": "Member 1", "Task": "Project kickoff", "Work Completed": "Defined scope and portal structure", "Evidence": "Kickoff notes", "Next Step": "Assign dataset review"},
    {"Date": "2026-05-03", "Member": "Member 2", "Task": "Data review", "Work Completed": "Loaded dataset tables and confirmed variables", "Evidence": "Schema summary", "Next Step": "Start cleaning plan"},
    {"Date": "2026-05-07", "Member": "Member 3", "Task": "Dashboard design", "Work Completed": "Outlined dashboard layout and key metrics", "Evidence": "Mockup plan", "Next Step": "Prepare placeholder visuals"},
]

st.table(logs)
