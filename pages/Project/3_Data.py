import streamlit as st
from utils.ui import section_header
from utils.data_loader import load_all_metadata

st.set_page_config(page_title="Data", initial_sidebar_state="expanded")

section_header("Data")

st.write(
    "This section documents the dataset structure, table relationships, and important variables for the e-commerce analytics workflow."
)

metadata = load_all_metadata()

st.subheader("Dataset overview")
for key, info in metadata.items():
    if 'error' in info:
        st.warning(f"Unable to load {info['file']}: {info['error']}")
        continue
    with st.expander(info['file']):
        st.write(f"Columns: {', '.join(info['columns'])}")
        st.write("Sample rows:")
        st.dataframe(info['sample'])

st.subheader("Important variables")
st.write(
    "Key variables include order timestamps, delivery dates, payment type, product category, buyer region, seller location, and review scores."
)

st.subheader("Relationships")
st.write(
    "The data is organized around orders, with lookup tables for customers, sellers, products, geolocation, payments, items, and reviews."
)

st.subheader("Data dictionary")
st.write(
    "The data dictionary is available through the expanded table views above. Each table lists its columns, sample rows, and inferred data types."
)

st.subheader("Data quality")
st.write(
    "Initial data quality checkpoints include missing values, duplicate order ids, date parsing readiness, and consistency across related tables."
)

st.subheader("Limitations")
st.write(
    "This portal currently presents structured data metadata and placeholders. Detailed analysis is pending data cleaning and integration steps."
)
