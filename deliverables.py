import streamlit as st


DELIVERABLES = [
    (
        "🌐",
        "Live dashboard",
        "Explore the deployed DVD Project Portal.",
        "https://dvd-project.streamlit.app/dashboard",
    ),
    (
        "⌘",
        "GitHub repository",
        "Browse the project source code, data work, and analysis files.",
        "https://github.com/DSAshv/DVDProject/tree/master",
    ),
    (
        "▤",
        "Technical report",
        "Read the project methodology, analysis, findings, and recommendations.",
        "https://github.com/DSAshv/DVDProject/blob/master/TECHNICAL_REPORT.pdf",
    ),
    (
        "▣",
        "Final presentation",
        "View the presentation of the project story and key insights.",
        "https://github.com/DSAshv/DVDProject/blob/master/PRESENTATION.pdf",
    ),
]


def render_deliverables_tab():
    st.markdown(
        """
        <style>
        .deliverables-page {
            --ink: #102a43;
            --muted: #52606d;
            --blue: #1d4ed8;
            --teal: #0f766e;
            --line: #dbe4ef;
            --soft: #eff6ff;
        }
        .deliverables-hero {
            color: #102a43;
            padding: 0;
            margin: 4px 0 14px;
        }
        .deliverables-hero h1 { margin: 0 0 3px; font-size: 24px; }
        .deliverables-hero p { margin: 0; color: #52606d; font-size: 13px; }
        .deliverable-kicker {
            color: #0f766e;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            margin: 0 0 3px;
        }
        .deliverable-icon {
            align-items: center;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            color: #1d4ed8;
            display: flex;
            font-size: 20px;
            height: 38px;
            justify-content: center;
            margin-bottom: 9px;
            width: 38px;
        }
        .deliverable-title { color: #102a43; margin: 0; font-size: 17px; }
        .deliverable-copy { color: #52606d; min-height: 32px; line-height: 1.3; margin: 4px 0 8px; font-size: 13px; }
        .deliverables-page [data-testid="stLinkButton"] a {
            background: #1d4ed8;
            border: 1px solid #1d4ed8;
            color: white;
            font-weight: 700;
            transition: background 150ms ease, border-color 150ms ease;
        }
        .deliverables-page [data-testid="stLinkButton"] a:hover {
            background: #0f766e;
            border-color: #0f766e;
            color: white;
        }
        </style>
        <div class="deliverables-page">
            <div class="deliverables-hero">
                <h1>Project Deliverables</h1>
                <p>One place for the live experience, project source, technical evidence, and final story.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(2)
    for index, (icon, title, description, url) in enumerate(DELIVERABLES):
        with columns[index % 2]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="deliverables-page">
                        <div class="deliverable-icon">{icon}</div>
                        <div class="deliverable-kicker">Deliverable {index + 1:02d}</div>
                        <h2 class="deliverable-title">{title}</h2>
                        <p class="deliverable-copy">{description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.link_button(f"Open {title}", url, use_container_width=True)