import streamlit as st


def render_home():
    st.markdown("""
    ### Project Introduction

    This project studies the complete e-commerce customer journey, from **order placement and payment to seller handling, delivery, and customer reviews**.

    Our goal is to understand what drives customer satisfaction and identify where the marketplace is at risk of poor experiences. We will investigate how **product categories, seller behaviour, delivery performance, and geographic regions** influence customer ratings.

    The ultimate objective is to help marketplace leadership **grow sales without compromising customer satisfaction**.
    """)

    st.divider()

    st.subheader("What We Will Do")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🔍 Explore
        - Understand the e-commerce datasets
        - Study orders, products, sellers and customers
        - Identify missing values and data-quality issues
        """)

    with col2:
        st.markdown("""
        #### 📊 Analyse
        - Analyse delivery and order performance
        - Compare customer satisfaction across segments
        - Identify patterns behind low and high ratings
        """)

    with col3:
        st.markdown("""
        #### 💡 Explain
        - Build explanatory visualizations
        - Identify marketplace risks
        - Translate findings into actionable recommendations
        """)

    st.divider()

    st.subheader("Key Questions We Aim to Answer")

    questions = [
        "Which product categories receive the highest and lowest customer ratings?",
        "How strongly does delivery performance affect customer satisfaction?",
        "Which seller behaviours are associated with poor customer experiences?",
        "Are certain regions or geographic patterns associated with delivery problems?",
        "Which parts of the order journey create the greatest risk of a one-star review?",
        "Where should the marketplace invest or intervene to improve customer experience?"
    ]

    for question in questions:
        st.markdown(f"• {question}")

    st.divider()

    st.subheader("Project Deliverables")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📈 Interactive Dashboard
        Explore customer satisfaction and marketplace risk by:

        - Category
        - Seller
        - Region
        - Delivery performance
        """)

    with col2:
        st.markdown("""
        ### 🎤 Final Presentation
        A focused story covering:

        - Business problem
        - Analytical approach
        - Key findings
        - Business implications
        - Recommended actions
        """)

    with col3:
        st.markdown("""
        ### 📄 Technical Report
        Complete documentation covering:

        - Data preparation
        - Exploratory analysis
        - Visualizations
        - Insights
        - Recommendations
        - Reproducible code
        """)

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
