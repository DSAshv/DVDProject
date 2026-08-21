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
# LOAD TASKS FROM JSON
# =========================================================

def load_tasks():

    try:

        if not os.path.exists(TASK_FILE):
            return []

        with open(
            TASK_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            tasks = json.load(file)

        if not isinstance(tasks, list):
            return []

        return tasks

    except (json.JSONDecodeError, OSError):
        return []


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
# STATUS BADGE
# =========================================================

def status_badge(status):

    styles = {

        "Completed": (
            "background:#dcfce7;"
            "color:#15803d;"
            "border:1px solid #bbf7d0;"
        ),

        "In Progress": (
            "background:#dbeafe;"
            "color:#1d4ed8;"
            "border:1px solid #bfdbfe;"
        ),

        "Pending": (
            "background:#fef3c7;"
            "color:#b45309;"
            "border:1px solid #fde68a;"
        ),

        "Not Started": (
            "background:#f3f4f6;"
            "color:#4b5563;"
            "border:1px solid #e5e7eb;"
        ),
    }

    style = styles.get(
        status,
        "background:#f3f4f6;color:#4b5563;border:1px solid #e5e7eb;"
    )

    return f"""
    <span class="status-badge" style="{style}">
        {status}
    </span>
    """


# =========================================================
# RENDER TASK TABLE
# =========================================================

def render_task_table(tasks):

    if not tasks:

        st.info(
            "No tasks found. Add tasks to tasks.json."
        )

        return

    # -----------------------------------------------------
    # BUILD TABLE ROWS
    # -----------------------------------------------------

    rows = ""

    for task in tasks:

        task_id = task.get("id", "")
        week = task.get("week", "")
        task_name = task.get("task", "")
        deadline = task.get("deadline", "")

        assignees = task.get(
            "assignees",
            []
        )

        if isinstance(assignees, list):
            assigned_to = ", ".join(assignees)
        else:
            assigned_to = str(assignees)

        status = task.get(
            "status",
            "Not Started"
        )

        rows += f"""
        <tr>

            <td class="id-cell">
                {task_id}
            </td>

            <td>
                <span class="week-badge">
                    {week}
                </span>
            </td>

            <td class="task-cell">
                {task_name}
            </td>

            <td class="deadline-cell">
                {deadline}
            </td>

            <td class="assignee-cell">
                {assigned_to}
            </td>

            <td>
                {status_badge(status)}
            </td>

        </tr>
        """

    # -----------------------------------------------------
    # TABLE HTML
    # -----------------------------------------------------

    table_html = f"""

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Arial,
                sans-serif;
        }}

        /* =================================================
           TABLE CONTAINER
        ================================================= */

        .task-table-wrapper {{

            width: 100%;

            border:
                1px solid #e5e7eb;

            border-radius: 16px;

            overflow: hidden;

            background: #ffffff;

            box-shadow:
                0 4px 18px
                rgba(0, 0, 0, 0.04);
        }}


        /* =================================================
           TABLE
        ================================================= */

        .task-table {{

            width: 100%;

            border-collapse: collapse;

            table-layout: fixed;

            font-family:
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Arial,
                sans-serif;
        }}


        /* =================================================
           HEADER
        ================================================= */

        .task-table thead {{

            background:
                #fafafa;
        }}

        .task-table th {{

            padding:
                14px 16px;

            text-align:
                left;

            font-size:
                11px;

            font-weight:
                750;

            text-transform:
                uppercase;

            letter-spacing:
                0.5px;

            color:
                #6b7280;

            border-bottom:
                1px solid #e5e7eb;
        }}


        /* =================================================
           BODY
        ================================================= */

        .task-table td {{

            padding:
                17px 16px;

            font-size:
                13px;

            color:
                #374151;

            border-bottom:
                1px solid #f0f0f0;

            vertical-align:
                middle;
        }}


        .task-table tbody tr:last-child td {{

            border-bottom:
                none;
        }}


        .task-table tbody tr {{

            transition:
                background 0.15s ease;
        }}


        .task-table tbody tr:hover {{

            background:
                #fffaf6;
        }}


        /* =================================================
           COLUMN WIDTHS
        ================================================= */

        .task-table th:nth-child(1),
        .task-table td:nth-child(1) {{

            width:
                55px;
        }}


        .task-table th:nth-child(2),
        .task-table td:nth-child(2) {{

            width:
                100px;
        }}


        .task-table th:nth-child(3),
        .task-table td:nth-child(3) {{

            width:
                34%;
        }}


        .task-table th:nth-child(4),
        .task-table td:nth-child(4) {{

            width:
                100px;
        }}


        .task-table th:nth-child(5),
        .task-table td:nth-child(5) {{

            width:
                25%;
        }}


        .task-table th:nth-child(6),
        .task-table td:nth-child(6) {{

            width:
                130px;
        }}


        /* =================================================
           ID
        ================================================= */

        .id-cell {{

            font-weight:
                750;

            color:
                #9ca3af !important;
        }}


        /* =================================================
           TASK
        ================================================= */

        .task-cell {{

            color:
                #111827 !important;

            font-weight:
                600;

            line-height:
                1.45;
        }}


        /* =================================================
           DEADLINE
        ================================================= */

        .deadline-cell {{

            font-weight:
                600;

            color:
                #4b5563 !important;

            white-space:
                nowrap;
        }}


        /* =================================================
           ASSIGNEES
        ================================================= */

        .assignee-cell {{

            color:
                #6b7280 !important;

            line-height:
                1.45;
        }}


        /* =================================================
           WEEK BADGE
        ================================================= */

        .week-badge {{

            display:
                inline-block;

            padding:
                5px 9px;

            border-radius:
                7px;

            background:
                #fff1e6;

            color:
                #d96d20;

            font-size:
                11px;

            font-weight:
                700;

            white-space:
                nowrap;
        }}


        /* =================================================
           STATUS
        ================================================= */

        .status-badge {{

            display:
                inline-block;

            padding:
                5px 10px;

            border-radius:
                999px;

            font-size:
                12px;

            font-weight:
                700;

            white-space:
                nowrap;
        }}


        /* =================================================
           MOBILE
        ================================================= */

        @media (max-width: 900px) {{

            .task-table th,
            .task-table td {{

                padding:
                    12px 10px;
            }}

            .task-table th:nth-child(5),
            .task-table td:nth-child(5) {{

                display:
                    none;
            }}

        }}

    </style>


    <div class="task-table-wrapper">

        <table class="task-table">

            <thead>

                <tr>

                    <th>
                        ID
                    </th>

                    <th>
                        Week
                    </th>

                    <th>
                        Task
                    </th>

                    <th>
                        Deadline
                    </th>

                    <th>
                        Assigned To
                    </th>

                    <th>
                        Status
                    </th>

                </tr>

            </thead>

            <tbody>

                {rows}

            </tbody>

        </table>

    </div>

    """

    # -----------------------------------------------------
    # CALCULATE HEIGHT
    # -----------------------------------------------------

    # Large enough to show all rows.
    # No internal scrollbar.

    table_height = (
        72 +
        (len(tasks) * 62)
    )

    # Safety limit so a huge JSON does not create
    # an absurdly tall iframe.

    table_height = min(
        table_height,
        3000
    )

    components.html(
        table_html,
        height=table_height,
        scrolling=False
    )


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

            box-sizing:
                border-box;

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


        /* =================================================
           TEAM HEADER
        ================================================= */

        .team-title {{

            margin-bottom:
                28px;
        }}


        .team-title h1 {{

            font-size:
                2.3rem;

            font-weight:
                750;

            margin:
                0;

            color:
                #111827;

            letter-spacing:
                -1px;
        }}


        .team-title p {{

            margin-top:
                7px;

            color:
                #6b7280;

            font-size:
                15px;
        }}


        .team-count {{

            display:
                inline-block;

            margin-top:
                10px;

            padding:
                6px 12px;

            border-radius:
                999px;

            background:
                #fff1e6;

            color:
                #e76f20;

            font-size:
                12px;

            font-weight:
                700;
        }}


        /* =================================================
           TEAM CARDS
        ================================================= */

        .team-grid {{

            display:
                grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(380px, 1fr)
                );

            gap:
                20px;

            margin-bottom:
                50px;
        }}


        .team-card {{

            position:
                relative;

            display:
                flex;

            align-items:
                center;

            gap:
                18px;

            padding:
                22px;

            border-radius:
                18px;

            background:
                rgba(
                    255,
                    255,
                    255,
                    0.92
                );

            border:
                1px solid #e5e7eb;

            box-shadow:
                0 4px 12px
                rgba(
                    0,
                    0,
                    0,
                    0.04
                );

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border-color 0.25s ease;

            overflow:
                hidden;
        }}


        .team-card::before {{

            content:
                "";

            position:
                absolute;

            left:
                0;

            top:
                0;

            bottom:
                0;

            width:
                4px;

            background:
                linear-gradient(
                    180deg,
                    #F58A3D,
                    #ffbd85
                );
        }}


        .team-card:hover {{

            transform:
                translateY(-6px);

            border-color:
                #f5b17a;

            box-shadow:
                0 15px 35px
                rgba(
                    0,
                    0,
                    0,
                    0.10
                );
        }}


        /* =================================================
           AVATAR
        ================================================= */

        .avatar {{

            flex-shrink:
                0;

            width:
                68px;

            height:
                68px;

            border-radius:
                50%;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            background:
                linear-gradient(
                    135deg,
                    #fff1e6,
                    #ffd7b5
                );

            color:
                #d96d20;

            font-size:
                20px;

            font-weight:
                750;

            border:
                3px solid white;

            box-shadow:
                0 4px 12px
                rgba(
                    0,
                    0,
                    0,
                    0.10
                );
        }}


        /* =================================================
           MEMBER INFO
        ================================================= */

        .member-info {{

            min-width:
                0;
        }}


        .member-info h3 {{

            margin:
                0 0 8px 0;

            font-size:
                17px;

            font-weight:
                700;

            color:
                #111827;
        }}


        .roll {{

            display:
                inline-block;

            padding:
                4px 8px;

            border-radius:
                6px;

            background:
                #f3f4f6;

            color:
                #4b5563;

            font-size:
                11px;

            font-weight:
                600;

            margin-bottom:
                8px;
        }}


        .email {{

            display:
                block;

            color:
                #6b7280;

            font-size:
                12px;

            text-decoration:
                none;

            overflow-wrap:
                anywhere;
        }}


        .email:hover {{

            color:
                #F58A3D;
        }}


        /* =================================================
           TASK SECTION
        ================================================= */

        .task-section {{

            margin-top:
                10px;
        }}


        .task-header {{

            display:
                flex;

            align-items:
                flex-end;

            justify-content:
                space-between;

            margin-bottom:
                18px;
        }}


        .task-header h2 {{

            margin:
                0;

            font-size:
                1.7rem;

            font-weight:
                750;

            color:
                #111827;

            letter-spacing:
                -0.5px;
        }}


        .task-header p {{

            margin:
                5px 0 0;

            color:
                #6b7280;

            font-size:
                13px;
        }}


        .task-badge {{

            padding:
                7px 12px;

            border-radius:
                999px;

            background:
                #fff1e6;

            color:
                #d96d20;

            font-size:
                12px;

            font-weight:
                700;
        }}


        /* =================================================
           MOBILE
        ================================================= */

        @media (max-width: 700px) {{

            .team-grid {{

                grid-template-columns:
                    1fr;
            }}


            .team-title h1 {{

                font-size:
                    2rem;
            }}


            .team-card {{

                padding:
                    18px;
            }}


            .task-header {{

                display:
                    block;
            }}


            .task-badge {{

                display:
                    inline-block;

                margin-top:
                    12px;
            }}

        }}

    </style>


    <div class="team-wrapper">


        <!-- =============================================
             TEAM HEADER
        ============================================== -->

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


        <!-- =============================================
             TEAM CARDS
        ============================================== -->

        <div class="team-grid">

            {cards}

        </div>


        <!-- =============================================
             TASK HEADER
        ============================================== -->

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
    # RENDER READ-ONLY TASK TABLE
    # =====================================================

    render_task_table(tasks)
