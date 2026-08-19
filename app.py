import streamlit as st

from home import render_home
from data_tab import render_data_tab
from team import render_team_tab
from business_goal import render_business_goal_tab


def main():
    st.set_page_config(
        page_title="DVD Project Portal For Team 2",
        layout="wide"
    )

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

    st.title("DVD Project Portal For Team 2")

    tabs = st.tabs([
        "Home",
        "Team",
        "Data",
        "Business Goal Questions",
    ])

    with tabs[0]:
        render_home()

    with tabs[1]:
        render_team_tab()

    with tabs[2]:
        render_data_tab()

    with tabs[3]:
        render_business_goal_tab()


if __name__ == "__main__":
    main()