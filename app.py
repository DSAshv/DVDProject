
import streamlit as st
from home import render_home
from data_tab import render_data_tab
from team import render_team_tab


def main():
    st.set_page_config(page_title="E-Commerce Project Portal", layout="wide")

    st.markdown(
        """
        <style>
            .main .block-container {
                padding-top: 0.5rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("E-Commerce Analysis — Project Portal")

    tabs = st.tabs(["Home", "Team", "Data"])

    with tabs[0]:
        render_home()

    with tabs[1]:
        render_team_tab()

    with tabs[2]:
        render_data_tab()


if __name__ == "__main__":
    main()
    
