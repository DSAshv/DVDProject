import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Business Problem", initial_sidebar_state="expanded")

section_header("Business Problem")

st.markdown(
    """
    The e-commerce marketplace is scaling quickly, but fast growth can expose gaps in delivery execution, seller fulfillment, and customer satisfaction.
    This project evaluates that growth vs experience tradeoff using orders, delivery timestamps, payments, and review outcomes.
    """
)

st.subheader("Business context")
st.write(
    "A fast-growing online marketplace must balance performance across logistics, seller behavior, and customer feedback. This dataset captures multiple stages of the order lifecycle for analysis."
)

st.subheader("Problem statement")
st.write(
    "Identify where delivery or seller processes are contributing to lower review scores, and support strategic decisions to improve customer satisfaction without slowing marketplace volume."
)

st.subheader("Business objective")
st.write(
    "Deliver actionable insights from order, delivery, and satisfaction data so the team can recommend targeted improvements for delivery reliability, seller performance, and category-level risk."
)

st.subheader("Key questions")
for q in [
    "Which factors are associated with poor customer ratings?",
    "How does delivery performance affect satisfaction?",
    "Which product categories have higher dissatisfaction?",
    "Which seller behaviours create risk?",
    "Which regions have delivery or satisfaction problems?",
    "Where should the company invest?",
    "Where should the company intervene?",
]:
    st.markdown(f"- {q}")
