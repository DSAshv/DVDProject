import streamlit as st

CSS = """
:root {
    --pg-orange: #F58D26;
    --pg-orange-light: #fff7ee;
    --pg-orange-mid: #ffe8cc;
    --pg-orange-dark: #c0620d;
    --pg-text-primary: #111827;
    --pg-text-secondary: #191b20;
    --pg-text-tertiary: #5f646d;
    --pg-border: #e5e7eb;
    --pg-border-light: #f3f4f6;
    --pg-bg: #ffffff;
    --pg-bg-soft: #f9fafb;
    --pg-radius: 12px;
    --pg-radius-sm: 8px;
    --pg-shadow: 0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(0,0,0,0.04);
}

body {
    color: var(--pg-text-primary);
    background-color: var(--pg-bg-soft);
}

.stApp {
    background-color: var(--pg-bg-soft);
}

.css-1d391kg {
    padding-top: 1rem;
}

[data-testid='stSidebar'] {
    background-color: var(--pg-bg);
    border-right: 1px solid var(--pg-border-light);
}

.stButton>button {
    background-color: var(--pg-orange);
    color: white;
    border: none;
    border-radius: var(--pg-radius-sm);
    padding: 0.8rem 1rem;
}

.stButton>button:hover {
    background-color: var(--pg-orange-dark);
}

.card {
    background: var(--pg-bg);
    border: 1px solid var(--pg-border);
    border-radius: var(--pg-radius);
    padding: 1.2rem;
    box-shadow: var(--pg-shadow);
    margin-bottom: 1rem;
}

.card-accent {
    border-left: 4px solid var(--pg-orange);
}

.section-title {
    font-size: 1.55rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.section-subtitle {
    color: var(--pg-text-tertiary);
    margin-bottom: 1rem;
}

.metric-small {
    color: var(--pg-text-secondary);
}

.table-container {
    background: var(--pg-bg);
    border: 1px solid var(--pg-border);
    border-radius: var(--pg-radius);
    padding: 1rem;
}
"""


def inject_style():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-subtitle'>{subtitle}</div>", unsafe_allow_html=True)


def section_header(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
