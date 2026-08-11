import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Team Members", initial_sidebar_state="expanded")

section_header("Team Members")

members = [
    {
        'name': 'Member 1',
        'role': 'Project Lead',
        'responsibilities': 'Project coordination, stakeholder communication, final deliverables.',
        'current_tasks': 'Oversee portal delivery, review technical report.',
        'github': 'https://github.com/example1',
    },
    {
        'name': 'Member 2',
        'role': 'Data Analyst',
        'responsibilities': 'Data preparation, exploratory analysis, statistics.',
        'current_tasks': 'Validate dataset joins and missing value handling.',
        'github': 'https://github.com/example2',
    },
    {
        'name': 'Member 3',
        'role': 'Visualization Designer',
        'responsibilities': 'Dashboard design, storyboarding, chart selection.',
        'current_tasks': 'Build dashboard placeholders and visualization narrative.',
        'github': 'https://github.com/example3',
    },
    {
        'name': 'Member 4',
        'role': 'Technical Writer',
        'responsibilities': 'Document findings, report drafting, presentation summary.',
        'current_tasks': 'Prepare report framework and presentation outline.',
        'github': 'https://github.com/example4',
    },
    {
        'name': 'Member 5',
        'role': 'Quality Assurance',
        'responsibilities': 'Review content quality, consistency, and portal usability.',
        'current_tasks': 'Verify navigation, page structure, and placeholder content.',
        'github': 'https://github.com/example5',
    },
]

for person in members:
    st.markdown(
        f"""
        <div class='card card-accent'>
            <strong>{person['name']}</strong>
            <p><strong>Role:</strong> {person['role']}</p>
            <p><strong>Responsibilities:</strong> {person['responsibilities']}</p>
            <p><strong>Current tasks:</strong> {person['current_tasks']}</p>
            <p><strong>GitHub:</strong> <a href='{person['github']}' target='_blank'>{person['github']}</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
