import streamlit as st
import streamlit.components.v1 as components


def render_team_tab():

    members = [
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

    cards = ""

    for m in members:
        cards += f"""
        <div class="team-card">

            <div class="avatar">
                {m['initial']}
            </div>

            <div class="member-info">
                <h3>{m['name']}</h3>

                <div class="roll">
                    {m['roll']}
                </div>

                <a class="email" href="mailto:{m['email']}">
                    {m['email']}
                </a>

            </div>

        </div>
        """

    # ---------------------------------------------------------
    # TASK SHEET
    # ---------------------------------------------------------


    task_rows = """

<tr class="kickoff-row">
    <td class="task-name">Kick off meeting</td>
    <td>09th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">All members</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>

<!-- WEEK 1 -->

<tr class="section-row">
    <td colspan="4">Week 1: (Data Exploration, Cleaning &amp; Initial Insights)</td>
</tr>

<tr>
    <td class="task-name">Understand the dataset, its structure, and key variables using the data dictionary</td>
    <td>10th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Yash</span>
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>

<tr>
    <td class="task-name">Rewrite the business goal in your own words and list the questions your analysis will answer.</td>
    <td>10th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Yash</span>
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>

<tr>
    <td class="task-name">Perform early exploratory checks to study borrower profiles and default proportions.</td>
    <td>12th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Yash</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>

<tr>
    <td class="task-name">Identify missing values, outliers, and data quality concerns.</td>
    <td>12th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>

<tr>
    <td class="task-name">Create a short Concept Note summarizing your plan and initial observations.</td>
    <td>15th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
        </div>
    </td>
    <td><span class="status completed">Completed</span></td>
</tr>


<!-- WEEK 2 -->

<tr class="section-row">
    <td colspan="4">Week 2: (Visualization &amp; Comparative Analysis)</td>
</tr>

<tr>
    <td class="task-name">Clean and preprocess the data, handle missing values, and resolve inconsistencies.</td>
    <td>18th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
        </div>
    </td>
    <td><span class="status in-progress">In Progress</span></td>
</tr>

<tr>
    <td class="task-name">Merge current and previous application files where required.</td>
    <td>To be clarified</td>
    <td>
        <div class="assignees">
            <span class="person pending">Pending</span>
        </div>
    </td>
    <td><span class="status pending-status">Pending</span></td>
</tr>

<tr>
    <td class="task-name">Perform detailed exploratory analysis on customer attributes, loan attributes and previous loan behavior.</td>
    <td>20th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Yash</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status in-progress">In Progress</span></td>
</tr>

<tr>
    <td class="task-name">Compare defaulters and non-defaulters using clear visual summaries.</td>
    <td>20th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Develop explanatory charts that start answering your analysis questions.</td>
    <td>20th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Prepare a mid-week EDA summary with your main findings so far.</td>
    <td>22nd Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Yash</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>


<!-- WEEK 3 -->

<tr class="section-row">
    <td colspan="4">Week 3: (Report Writing &amp; Final Presentation)</td>
</tr>

<tr>
    <td class="task-name">Build a clean and interactive dashboard that presents your insights in a structured way.</td>
    <td>24th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Ashwanth V</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Write a complete technical report covering your approach, analysis and key takeaways.</td>
    <td>24th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Ashwanth V</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Prepare a final presentation with focused visuals and clear conclusions.</td>
    <td>28th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Review your work within the group and refine charts, text and explanations.</td>
    <td>28th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Yash</span>
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

<tr>
    <td class="task-name">Present your insights with a simple story that connects the problem, analysis and actions.</td>
    <td>28th Aug</td>
    <td>
        <div class="assignees">
            <span class="person">Sahib</span>
            <span class="person">Yash</span>
            <span class="person">Kannan</span>
            <span class="person">Ashwanth V</span>
            <span class="person">Anushka</span>
        </div>
    </td>
    <td><span class="status not-started">Not Started</span></td>
</tr>

"""
    # ---------------------------------------------------------
    # HTML
    # ---------------------------------------------------------

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

    /* ================= TEAM HEADER ================= */

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


    /* ================= TEAM CARDS ================= */

    .team-grid {{
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(280px, 1fr));
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

        background: rgba(255,255,255,0.92);

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

        background: linear-gradient(
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

        background: linear-gradient(
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


    /* ================= TASK SHEET ================= */

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


    /* ================= TABLE ================= */

    .table-container {{
        width: 100%;

        overflow-x: auto;

        border: 1px solid #d9dde3;

        border-radius: 10px;

        background: white;

        box-shadow:
            0 3px 12px rgba(0,0,0,0.04);
    }}

    .task-table {{
        width: 100%;

        min-width: 850px;

        border-collapse: collapse;

        table-layout: fixed;
    }}

    .task-table th,
    .task-table td {{
        border-right: 1px solid #d9dde3;

        border-bottom: 1px solid #d9dde3;

        padding: 10px 12px;

        font-size: 13px;

        color: #171717;

        vertical-align: middle;
    }}

    .task-table th:last-child,
    .task-table td:last-child {{
        border-right: none;
    }}

    .task-table tr:last-child td {{
        border-bottom: none;
    }}

    .task-table th {{
        background: #fafafa;

        font-weight: 700;

        text-align: left;

        color: #222;
    }}


   .task-table th:first-child,
    .task-table td:first-child {{
        width: 48%;
        text-align: left;
    }}

    .task-table th:nth-child(2),
    .task-table td:nth-child(2) {{
        width: 13%;
        text-align: center;
    }}

    .task-table th:nth-child(3),
    .task-table td:nth-child(3) {{
        width: 27%;
        text-align: left;
    }}

    .task-table th:nth-child(4),
    .task-table td:nth-child(4) {{
        width: 12%;
        text-align: center;
    }}

    /* ================= STATUS ================= */

.status {{
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 5px 9px;

    border-radius: 999px;

    font-size: 11px;
    font-weight: 700;

    white-space: nowrap;
}}

.status::before {{
    content: "";

    width: 6px;
    height: 6px;

    border-radius: 50%;

    margin-right: 6px;

    background: currentColor;
}}

.status.completed {{
    background: #eaf7ef;
    color: #16834a;
}}

.status.in-progress {{
    background: #fff4df;
    color: #c87800;
}}

.status.not-started {{
    background: #f3f4f6;
    color: #6b7280;
}}

.status.pending-status {{
    background: #fff3cd;
    color: #856404;
}}

    /* ================= TASK TEXT ================= */

    .task-name {{
        line-height: 1.4;

        font-weight: 500;

        color: #1f2937;
    }}


    /* ================= ASSIGNEES ================= */

    .assignees {{
        display: flex;

        flex-wrap: wrap;

        gap: 5px;

        align-items: center;
    }}

    .person {{
        display: inline-flex;

        align-items: center;

        padding: 4px 8px;

        border-radius: 6px;

        background: #f3f4f6;

        color: #374151;

        font-size: 11px;

        font-weight: 600;

        white-space: nowrap;
    }}

    .person::before {{
        content: "•";

        margin-right: 5px;

        color: #F58A3D;

        font-size: 12px;
    }}

    .person.pending {{
        background: #fff3cd;

        color: #856404;
    }}

    .person.pending::before {{
        color: #d99a00;
    }}


    /* ================= WEEK SECTION ================= */

    .section-row td {{
        background: #faf9ff;

        color: #27205d;

        font-weight: 750;

        font-size: 15px;

        text-align: left !important;

        padding: 9px 12px;
    }}


    /* ================= KICK OFF ================= */

    .kickoff-row td {{
        background: #ffffff;
    }}

    .kickoff-row .task-name {{
        color: #4285f4;

        font-weight: 600;

        font-size: 14px;
    }}


    /* ================= HOVER ================= */

    .task-table tbody tr:not(.section-row):hover td {{
        background: #fffaf6;
    }}

    .task-table tbody tr.section-row:hover td {{
        background: #faf9ff;
    }}

    .task-table tbody tr:hover .person {{
        background: #fff1e6;

        color: #c45f18;
    }}

    .task-table tbody tr:hover .person.pending {{
        background: #fff3cd;

        color: #856404;
    }}

    


    /* ================= MOBILE ================= */

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

        .task-table {{
            min-width: 750px;
        }}

    }}

</style>



    <div class="team-wrapper">

        <!-- ================= TEAM ================= -->

        <div class="team-title">
            <h1>Our Team 2</h1>
            <p>Project Group 2 · IIT Madras BS in Data Science</p>
            <span class="team-count">● 5 Members</span>
        </div>

        <div class="team-grid">
            {cards}
        </div>


        <!-- ================= TASK SHEET ================= -->

        <div class="task-section">

            <div class="task-header">

                <div>
                    <h2> Project Task Sheet</h2>
                    <p>
                        Team responsibilities, deadlines and project milestones
                    </p>
                </div>

                <div class="task-badge">
                    3 Week Roadmap
                </div>

            </div>

            <div class="table-container">

                <table class="task-table">

                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Deadline</th>
                            <th>Assigned To</th>
                            <th>Status</th>
                        </tr>
                    </thead>

                    <tbody>
                        {task_rows}
                    </tbody>

                </table>

            </div>

        </div>

    </div>
    """

    components.html(
        html,
        height=1800,
        scrolling=False
    )