import streamlit as st


def render_home():
    st.markdown("""
    ### Project Introduction

    This project studies the complete e-commerce customer journey, from **order placement and payment to seller handling, delivery, and customer reviews**.

    Our goal is to understand what drives customer satisfaction and identify where the marketplace is at risk of poor experiences. We will investigate how **product categories, seller behaviour, delivery performance, and geographic regions** influence customer ratings.

    The ultimate objective is to help marketplace leadership **grow sales without compromising customer satisfaction**.
    """)

    st.divider()


    st.subheader("Project Deliverables")
    st.subheader("1. E-Commerce Analytics Project")

    st.markdown(
        """
    - [ ] Build an end-to-end e-commerce analytics project
        - [ ] Create an interactive dashboard to explore customer satisfaction and marketplace risk
        - [ ] Analyze category, seller, region, and delivery-performance drivers
        - [ ] Identify actionable business insights for marketplace improvement
    """
    )

    st.subheader("2. Final Presentation")

    st.markdown(
        """
    - [ ] Prepare the final presentation
        - [ ] Explain the business problem and analytical approach
        - [ ] Present key findings and business implications
        - [ ] Recommend next steps and actions
    """
    )

    st.subheader("3. Technical Report")

    st.markdown(
        """
    - [ ] Deliver the technical report
        - [ ] Document data preparation and exploratory analysis
        - [ ] Summarize visualizations, insights, and recommendations
        - [ ] Include reproducible code and methodology
    """
    )

    st.divider()

    st.subheader("Project Timeline")

    st.markdown("""
    **Week 1 · Explore & Prepare**  
    Understand the datasets, define analysis questions, perform initial exploration, and identify data-quality issues.

    **Week 2 · Analyse & Visualize**  
    Clean the data, perform detailed analysis, compare customer segments, and develop explanatory visualizations.

    **Week 3 · Build & Present**  
    Build the interactive dashboard, finalize the technical report, prepare the presentation, and refine the project story.
    """)
