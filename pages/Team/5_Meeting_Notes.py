import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Meeting Notes")

section_header("Meeting Notes")

notes = [
    {
        "Date": "2026-05-02",
        "Attendees": "Member 1, Member 2, Member 3",
        "Discussion": "Project goals, dataset scope, deliverable structure.",
        "Decisions": "Use Streamlit portal, focus on clear storytelling and dashboard placeholder.",
        "Assigned tasks": "Data load, UI structure, content placeholders.",
        "Deadlines": "Week 1 for data structure and pages.",
        "Blockers": "Dataset path and loading details.",
        "Next meeting": "Review page structure and dataset dictionary.",
    },
]

st.table(notes)
