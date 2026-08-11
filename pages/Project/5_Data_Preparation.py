import streamlit as st
from utils.ui import section_header

st.set_page_config(page_title="Data Preparation", initial_sidebar_state="expanded")

section_header("Data Preparation")

st.write(
    "This section will summarize the cleaning steps required to make the e-commerce dataset analysis-ready."
)

st.markdown("### Missing values")
st.write("Track missing values across purchase, delivery, review, and seller tables.")

st.markdown("### Duplicates")
st.write("Check duplicate order_id, customer_id, product_id, and seller_id records to prevent inflated summaries.")

st.markdown("### Invalid records")
st.write("Validate date sequences, order status values, payment amounts, and review entries.")

st.markdown("### Data types")
st.write("Convert timestamps to datetime, numeric fields to float/int, and categorical fields to category-like values.")

st.markdown("### Date handling")
st.write("Align order purchase, approval, carrier departure, and customer delivery dates for lead-time and delay metrics.")

st.markdown("### Outliers")
st.write("Inspect extreme prices, freight values, product dimensions, and delivery lead times.")

st.markdown("### Joins")
st.write("Join orders with customers, items, products, sellers, payments, and reviews to build the final analytical dataset.")

st.markdown("### Feature engineering")
st.write("Create delivery delay, fulfillment speed, price segments, category risk flags, and satisfaction labels.")

st.markdown("### Final analytical dataset")
st.write("The outcome will be a consolidated dataset keyed by order_id with joined order, delivery, seller, product, region, payment, and review data.")
