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
                {m["initial"]}
            </div>

            <div class="member-info">

                <h3>{m["name"]}</h3>

                <div class="roll">
                    {m["roll"]}
                </div>

                <a class="email" href="mailto:{m["email"]}">
                    {m["email"]}
                </a>

            </div>

        </div>
        """

    html = f"""
    <style>

        .team-wrapper {{
            width: 100%;
            padding: 10px 0 30px 0;
        }}

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

        .team-grid {{
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
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

        @media (max-width: 600px) {{

            .team-grid {{
                grid-template-columns: 1fr;
            }}

            .team-title h1 {{
                font-size: 2rem;
            }}

            .team-card {{
                padding: 18px;
            }}
        }}

    </style>

    <div class="team-wrapper">

        <div class="team-title">
            <h1>Our Team 2</h1>
            <p>Project Group 2 · IIT Madras BS in Data Science</p>
            <span class="team-count">● 5 Members</span>
        </div>

        <div class="team-grid">
            {cards}
        </div>

    </div>
    """

    components.html(html, height=700, scrolling=True)