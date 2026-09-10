import streamlit as st

from dashboard import render_dashboard


st.set_page_config(
    page_title="Marketplace Growth Dashboard",
    page_icon="📈",
    layout="wide",
)
st.set_option("client.showSidebarNavigation", False)

render_dashboard()