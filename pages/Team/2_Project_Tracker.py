import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Project Tracker", initial_sidebar_state="expanded")

section_header("Project Tracker")
col1, col2, col3 = st.columns(3)
col1.metric("Completed", "2/12")
col2.metric("In progress", "4")
col3.metric("On track", "Yes")

st.write("This tracker table is designed to update with task owners, deadlines, and status for the project workflow.")

tasks = [
    {"Task": "Data exploration", "Owner": "Member 2", "Status": "In Progress", "Deadline": "Week 1", "Deliverable": "Data quality notes"},
    {"Task": "Visualization planning", "Owner": "Member 3", "Status": "In Progress", "Deadline": "Week 2", "Deliverable": "Storyboarding"},
    {"Task": "Dashboard layout", "Owner": "Member 3", "Status": "Not Started", "Deadline": "Week 3", "Deliverable": "Dashboard mockup"},
    {"Task": "Final report", "Owner": "Member 4", "Status": "Not Started", "Deadline": "Week 3", "Deliverable": "Technical report draft"},
    {"Task": "Quality review", "Owner": "Member 5", "Status": "Not Started", "Deadline": "Week 3", "Deliverable": "Portal review checklist"},
]

st.table(tasks)
