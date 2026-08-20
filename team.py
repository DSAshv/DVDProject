import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import os


# =========================================================
# CONFIG
# =========================================================

TASK_FILE = "tasks.json"


# =========================================================
# TEAM MEMBERS
# =========================================================

MEMBERS = [
    {
        "name": "Sahib Randhawa",
        "roll": "21F1006116",
        "email": "21f1006116@ds.study.iitm.ac.in",
        "initial": "SR",
    },
    {
        "name": "Yash Arabhavi",
        "roll": "22F3001882",
        "email": "22f3001882@ds.study.iitm.ac.in",
        "initial": "YA",
    },
    {
        "name": "Anushka",
        "roll": "21F1003889",
        "email": "21f1003889@ds.study.iitm.ac.in",
        "initial": "A",
    },
    {
        "name": "Ashwanth V",
        "roll": "22F3001662",
        "email": "22f3001662@ds.study.iitm.ac.in",
        "initial": "AV",
    },
    {
        "name": "Kannan S",
        "roll": "21F3000990",
        "email": "21f3000990@ds.study.iitm.ac.in",
        "initial": "KS",
    },
]


# =========================================================
# DEFAULT TASKS
# =========================================================
# Used only if tasks.json doesn't exist or cannot be read.
# You can remove/change these based on your actual project.
# =========================================================

DEFAULT_TASKS = [
    {
        "id": 1,
        "week": "Kickoff",
        "week_title": "Project Kickoff",
        "task": "Finalize project topic and understand the problem statement",
        "deadline": "Aug 20",
        "assignees": ["All Members"],
        "status": "Completed",
    },
    {
        "id": 2,
        "week": "Week 1",
        "week_title": "Data Exploration & Cleaning",
        "task": "Explore the dataset and understand all available fields",
        "deadline": "Aug 22",
        "assignees": ["Ashwanth V", "Yash Arabhavi"],
        "status": "In Progress",
    },
    {
        "id": 3,
        "week": "Week 1",
        "week_title": "Data Exploration & Cleaning",
        "task": "Clean missing values and prepare the data for analysis",
        "deadline": "Aug 23",
        "assignees": ["Sahib Randhawa", "Anushka"],
        "status": "Not Started",
    },
    {
        "id": 4,
        "week": "Week 1",
        "week_title": "Data Exploration & Cleaning",
        "task": "Create data dictionary and document important variables",
        "deadline": "Aug 24",
        "assignees": ["Kannan S", "Ashwanth V"],
        "status": "Not Started",
    },
    {
        "id": 5,
        "week": "Week 2",
        "week_title": "Visualization & Comparative Analysis",
        "task": "Identify important customer satisfaction patterns",
        "deadline": "Aug 26",
        "assignees": ["All Members"],
        "status": "Not Started",
    },
    {
        "id": 6,
        "week": "Week 2",
        "week_title": "Visualization & Comparative Analysis",
        "task": "Design charts for delivery performance and customer ratings",
        "deadline": "Aug 28",
        "assignees": ["Yash Arabhavi", "Anushka"],
        "status": "Pending",
    },
    {
        "id": 7,
        "week": "Week 3",
        "week_title": "Report & Presentation",
        "task": "Prepare final report",
        "deadline": "Aug 30",
        "assignees": ["Sahib Randhawa", "Kannan S"],
        "status": "Not Started",
    },
    {
        "id": 8,
        "week": "Week 3",
        "week_title": "Report & Presentation",
        "task": "Prepare final presentation and rehearse",
        "deadline": "Sep 01",
        "assignees": ["All Members"],
        "status": "Not Started",
    },
]


# =========================================================
# LOAD / SAVE TASKS
# =========================================================

def load_tasks():

    try:

        if not os.path.exists(TASK_FILE):
            save_tasks(DEFAULT_TASKS)
            return DEFAULT_TASKS.copy()

        with open(
            TASK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            tasks = json.load(file)

        # Make sure every task has a status
        for task in tasks:

            if "status" not in task:
                task["status"] = "Not Started"

        return tasks

    except (json.JSONDecodeError, OSError):

        return DEFAULT_TASKS.copy()


def save_tasks(tasks):

    with open(
        TASK_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tasks,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# STATUS HELPERS
# =========================================================

STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Completed",
    "Pending",
]


# =========================================================
# RENDER TEAM CARDS
# =========================================================

def render_team_cards():

    cards = ""

    for member in MEMBERS:

        cards += f"""
        <div class="team-card">

            <div class="avatar">
                {member['initial']}
            </div>

            <div class="member-info">

                <h3>
                    {member['name']}
                </h3>

                <div class="roll">
                    {member['roll']}
                </div>

                <a
                    class="email"
                    href="mailto:{member['email']}"
                >
                    {member['email']}
                </a>

            </div>

        </div>
        """

    return cards


# =========================================================
# INLINE TASK TABLE
# =========================================================

def render_task_table(tasks):

    if not tasks:

        st.info("No tasks found.")

        return


    # -----------------------------------------------------
    # BUILD DATAFRAME
    # -----------------------------------------------------

    table_data = []

    for task in tasks:

        table_data.append(
            {
                "ID": task["id"],

                "Week": task["week"],

                "Task": task["task"],

                "Deadline": task["deadline"],

                "Assigned To": ", ".join(
                    task["assignees"]
                ),

                "Status": task.get(
                    "status",
                    "Not Started"
                ),
            }
        )


    df = pd.DataFrame(table_data)


    # -----------------------------------------------------
    # INLINE EDITABLE TABLE
    # -----------------------------------------------------

    # Height based on number of rows
    table_height = min(
        1200,
        max(
            180,
            55 * (len(df) + 1)
        )
    )

    edited_df = st.data_editor(

        df,

        row_height=50,

        height=table_height,

        hide_index=True,

        use_container_width=True,

        column_config={

            "ID": st.column_config.NumberColumn(
                "ID",
                disabled=True,
                width="small",
            ),

            "Week": st.column_config.TextColumn(
                "Week",
                disabled=True,
                width="small",
            ),

            "Task": st.column_config.TextColumn(
                "Task",
                disabled=True,
                width="large",
            ),

            "Deadline": st.column_config.TextColumn(
                "Deadline",
                disabled=True,
                width="medium",
            ),

            "Assigned To": st.column_config.TextColumn(
                "Assigned To",
                disabled=True,
                width="medium",
            ),

            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=STATUS_OPTIONS,
                required=True,
                width="medium",
            ),
        },

        disabled=[
            "ID",
            "Week",
            "Task",
            "Deadline",
            "Assigned To",
        ],

        key="task_table_editor",
    )


    # -----------------------------------------------------
    # DETECT STATUS CHANGES
    # -----------------------------------------------------

    changed = False

    for index, row in edited_df.iterrows():

        task_id = row["ID"]

        new_status = row["Status"]


        for task in tasks:

            if task["id"] == task_id:

                old_status = task.get(
                    "status",
                    "Not Started"
                )


                if old_status != new_status:

                    task["status"] = new_status

                    changed = True

                break


    # -----------------------------------------------------
    # SAVE CHANGES
    # -----------------------------------------------------

    if changed:

        save_tasks(tasks)

        st.toast(
            "Task status updated successfully",
            icon="✅",
        )

        st.rerun()


# =========================================================
# MAIN TEAM TAB
# =========================================================

def render_team_tab():

    # =====================================================
    # LOAD TASKS
    # =====================================================

    tasks = load_tasks()


    # =====================================================
    # TEAM CARDS
    # =====================================================

    cards = render_team_cards()


    # =====================================================
    # PAGE HTML
    # =====================================================

    html = f"""

    <style>

        * {{
            box-sizing: border-box;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Helvetica,
                Arial,
                sans-serif !important;
        }}


        /* ================================================
           TEAM HEADER
        ================================================ */

        .team-title {{
            margin-bottom: 28px;
        }}

        .team-title h1 {{
            font-size: 2.3rem;

            font-weight: 750;

            margin: 0;

            color: #111827;

            letter-spacing: -1px;
        }}

        .team-title p {{
            margin-top: 7px;

            color: #6b7280;

            font-size: 15px;
        }}

        .team-count {{
            display: inline-block;

            margin-top: 10px;

            padding: 6px 12px;

            border-radius: 999px;

            background: #fff1e6;

            color: #e76f20;

            font-size: 12px;

            font-weight: 700;
        }}


        /* ================================================
           TEAM CARDS
        ================================================ */

        .team-grid {{
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(380px, 1fr));

            gap: 20px;

            margin-bottom: 50px;
        }}

        .team-card {{
            position: relative;

            display: flex;

            align-items: center;

            gap: 18px;

            padding: 22px;

            border-radius: 18px;

            background:
                rgba(255,255,255,0.92);

            border: 1px solid #e5e7eb;

            box-shadow:
                0 4px 12px rgba(0,0,0,0.04);

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border-color 0.25s ease;

            overflow: hidden;
        }}

        .team-card::before {{
            content: "";

            position: absolute;

            left: 0;

            top: 0;

            bottom: 0;

            width: 4px;

            background:
                linear-gradient(
                    180deg,
                    #F58A3D,
                    #ffbd85
                );
        }}

        .team-card:hover {{
            transform: translateY(-6px);

            border-color: #f5b17a;

            box-shadow:
                0 15px 35px rgba(0,0,0,0.10);
        }}

        .avatar {{
            flex-shrink: 0;

            width: 68px;

            height: 68px;

            border-radius: 50%;

            display: flex;

            align-items: center;

            justify-content: center;

            background:
                linear-gradient(
                    135deg,
                    #fff1e6,
                    #ffd7b5
                );

            color: #d96d20;

            font-size: 20px;

            font-weight: 750;

            border: 3px solid white;

            box-shadow:
                0 4px 12px rgba(0,0,0,0.10);
        }}

        .member-info {{
            min-width: 0;
        }}

        .member-info h3 {{
            margin: 0 0 8px 0;

            font-size: 17px;

            font-weight: 700;

            color: #111827;
        }}

        .roll {{
            display: inline-block;

            padding: 4px 8px;

            border-radius: 6px;

            background: #f3f4f6;

            color: #4b5563;

            font-size: 11px;

            font-weight: 600;

            margin-bottom: 8px;
        }}

        .email {{
            display: block;

            color: #6b7280;

            font-size: 12px;

            text-decoration: none;

            overflow-wrap: anywhere;
        }}

        .email:hover {{
            color: #F58A3D;
        }}


        /* ================================================
           TASK SECTION
        ================================================ */

        .task-section {{
            margin-top: 10px;
        }}

        .task-header {{
            display: flex;

            align-items: flex-end;

            justify-content: space-between;

            margin-bottom: 18px;
        }}

        .task-header h2 {{
            margin: 0;

            font-size: 1.7rem;

            font-weight: 750;

            color: #111827;

            letter-spacing: -0.5px;
        }}

        .task-header p {{
            margin: 5px 0 0;

            color: #6b7280;

            font-size: 13px;
        }}

        .task-badge {{
            padding: 7px 12px;

            border-radius: 999px;

            background: #fff1e6;

            color: #d96d20;

            font-size: 12px;

            font-weight: 700;
        }}


        /* ================================================
           STREAMLIT DATA EDITOR
        ================================================ */


        /* ================================================
           MOBILE
        ================================================ */

        @media (max-width: 700px) {{

            .team-grid {{
                grid-template-columns: 1fr;
            }}

            .team-title h1 {{
                font-size: 2rem;
            }}

            .team-card {{
                padding: 18px;
            }}

            .task-header {{
                display: block;
            }}

            .task-badge {{
                display: inline-block;

                margin-top: 12px;
            }}

        }}

    </style>


    <div class="team-wrapper">


        <!-- ============================================
             TEAM HEADER
        ============================================ -->

        <div class="team-title">

            <h1>
                Team #2
            </h1>

            <p>
                Project Group 2 · IIT Madras BS in Data Science
            </p>

            <span class="team-count">
                ● 5 Members
            </span>

        </div>


        <!-- ============================================
             TEAM CARDS
        ============================================ -->

        <div class="team-grid">

            {cards}

        </div>


        <!-- ============================================
             TASK HEADER
        ============================================ -->

        <div class="task-section">

            <div class="task-header">

                <div>

                    <h2>
                        Project Task Sheet
                    </h2>

                    <p>
                        Team responsibilities, deadlines and
                        project milestones
                    </p>

                </div>

                <div class="task-badge">

                    3 Week Roadmap

                </div>

            </div>

        </div>

    </div>

    """


    # =====================================================
    # RENDER TEAM HTML
    # =====================================================

    components.html(
        html,
        height=620,
        scrolling=False,
    )


    # =====================================================
    # RENDER EDITABLE TASK TABLE
    # =====================================================

    render_task_table(tasks)