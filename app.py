import streamlit as st
from utils.ui import inject_style, page_header, section_header

st.set_page_config(
    page_title="E-Commerce Visualization Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_style()

with st.sidebar:
    st.title("Project portal")
    selected_section = st.radio(
        "Navigation",
        [
            "Home",
            "Project Overview",
            "Business Problem",
            "Data",
            "Interactive Dashboard",
            "Team Members",
            "Resources",
        ],
    )
    st.markdown("---")
    st.markdown(
        "**Project navigation**\n- Project Overview\n- Business Problem\n- Data\n- Dashboard\n- Team pages"
    )

page_header(
    "A Visual Study of E-Commerce Orders, Delivery & Customer Satisfaction",
    "Understanding how orders, sellers, delivery performance, geography, and customer experience interact across the e-commerce journey.",
)

section_header("Project at a glance")
tab1, tab2, tab3 = st.tabs(["Overview", "Quick links", "Status"])
with tab1:
    st.write(
        "This portal is the central workspace for the e-commerce visualization project, combining documentation, team planning, and a future dashboard in a single Streamlit app."
    )
    st.write(
        "The pages in the sidebar contain the project narrative, data planning, analysis placeholders, and team coordination details."
    )
with tab2:
    st.write("Use the sidebar to open the sections below:")
    st.markdown("- Project Overview and planning pages")
    st.markdown("- Data dictionary and analysis placeholders")
    st.markdown("- Interactive Dashboard and presentation pages")
    st.markdown("- Team members, tracker, roadmap, work logs, meeting notes and resources")
with tab3:
    col1, col2, col3 = st.columns([2, 1, 1])
    col1.metric("Project status", "In progress", "May 2026")
    col2.metric("Duration", "3 weeks")
    col3.metric("Dataset", "Brazilian E-Commerce Dataset")

section_header("Start your review")
button_col, info_col = st.columns([1, 2])
if button_col.button("Explore Project"):
    st.info("Open the Project section from the sidebar to continue with the project workflow.")
if button_col.button("View Interactive Dashboard"):
    st.info("Open the Interactive Dashboard page from the sidebar to view the future dashboard layout.")

info_col.markdown(
    """
    **Key portal sections**
    - Project planning and strategy
    - Data and analysis readiness
    - Visualization story and recommendations
    - Team coordination and documentation
    """
)
