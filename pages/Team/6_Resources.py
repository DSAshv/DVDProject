import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Resources")

section_header("Resources")

resources = [
    {"Name": "Dataset", "Link": "Dataset/E-Commerce Dataset ", "Type": "Local files"},
    {"Name": "Data dictionary", "Link": "#", "Type": "Portal metadata"},
    {"Name": "Notebooks", "Link": "#", "Type": "Planned"},
    {"Name": "Dashboard", "Link": "#", "Type": "Interactive placeholder"},
    {"Name": "Presentation", "Link": "#", "Type": "Planned"},
    {"Name": "Technical report", "Link": "#", "Type": "Planned"},
]

st.table(resources)
