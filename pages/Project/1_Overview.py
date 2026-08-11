import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Project Overview")

section_header("Project Overview")
st.write(
    "This project explores customer satisfaction across order, payment, seller handling, freight, delivery, and review cycles for a Brazilian e-commerce dataset."
)

st.markdown(
    """
    **Customer journey**

    Order
    ↓
    Payment
    ↓
    Seller Handling
    ↓
    Freight
    ↓
    Delivery
    ↓
    Customer Review
    ↓
    Satisfaction
    """
)

st.subheader("Business objective")
st.write(
    "Understand key delivery and satisfaction drivers to support data-driven recommendations for marketplace operations, seller performance, and customer experience."
)

st.subheader("Major business questions")
cols = st.columns(3)
questions = [
    "Which factors are associated with poor customer ratings?",
    "How does delivery performance affect satisfaction?",
    "Which product categories have higher dissatisfaction?",
    "Which seller behaviours create risk?",
    "Which regions have delivery or satisfaction problems?",
    "Where should the company invest or intervene?",
]
for idx, question in enumerate(questions):
    with cols[idx % 3]:
        st.markdown(f"<div class='card card-accent'><strong>{question}</strong></div>", unsafe_allow_html=True)
