import os
import json

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import streamlit.components.v1 as components
import pydeck as pdk
from scipy.stats import pointbiserialr


DATA_DIR = "processed_data"
REPORTS = {
    "Delivery promise": ("Yash Arabhavi", "analysis/Yash/Delivery_Performance_Report.pdf"),
    "Seller performance": ("Kannan S", "analysis/Kannan/Seller_Performance_Report.pdf"),
    "Regional logistics": ("Anushka", "analysis/Anushka/Regional_Logistics_Report.pdf"),
    "Product portfolio": ("Ashwanth V", "analysis/Ashwanth/Product_Pricing_Analysis.pdf"),
    "Seller behaviour": ("Sahib Randhawa", "analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf"),
}

INTRO_CATEGORIES = {
    "Delivery performance": {
        "owner": "Yash Arabhavi",
        "color": "#0891b2",
        "questions": [
            "How strongly does delivery lateness predict a bad review, and where is the cliff edge?",
            "Is it being slow or breaking the promise that angers customers more?",
        ],
    },
    "Regional logistics": {
        "owner": "Anushka",
        "color": "#2563eb",
        "questions": [
            "Do certain regions experience systematically worse delivery performance and satisfaction?",
            "Which seller-state to customer-state routes perform worst?",
        ],
    },
    "Seller performance": {
        "owner": "Kannan S",
        "color": "#059669",
        "questions": [
            "How concentrated is the damage across sellers, especially the worst 5%?",
            "Are certain sellers a recurring source of bad experiences?",
        ],
    },
    "Seller behaviour drivers": {
        "owner": "Sahib Randhawa",
        "color": "#d97706",
        "questions": [
            "Which seller behaviours predict bad reviews: handling time, volume, catalogue breadth, or freight pricing?",
            "Where should the company invest to grow while preserving satisfaction?",
        ],
    },
    "Product and pricing": {
        "owner": "Ashwanth V",
        "color": "#db2777",
        "questions": [
            "Beyond delivery, what else moves the score: price, freight, product attributes, or order size?",
            "Which product categories carry high revenue and poor satisfaction?",
        ],
    },
}


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_master():
    path = os.path.join(DATA_DIR, "master_orders.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    for column in ["is_late", "is_negative", "is_multi_seller", "is_interstate"]:
        if column in df:
            df[column] = df[column].map({"True": True, "False": False, True: True, False: False})
            df[column] = df[column].astype("boolean")
    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce", format="mixed"
    )
    for column in ["review_score", "total_price", "total_freight", "delay_days", "delivery_days", "handling_days", "transit_days"]:
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def reviewed_delivered(df):
    return df[(df["order_status"] == "delivered") & df["is_negative"].notna()].copy()


def rate_table(frame, group, label):
    result = frame.groupby(group, dropna=False).agg(
        Orders=("order_id", "count"),
        Negative=("is_negative", "mean"),
        GMV=("total_price", "sum"),
    ).reset_index().rename(columns={group: label})
    result["Negative rate"] = (pd.to_numeric(result.pop("Negative"), errors="coerce") * 100).round(1)
    result["GMV"] = pd.to_numeric(result["GMV"], errors="coerce").round(0)
    return result


def numeric_chart(frame, columns):
    chart = frame.loc[:, columns].copy()
    for column in columns:
        chart[column] = pd.to_numeric(chart[column], errors="coerce").fillna(0.0).astype(float)
    return chart


# --------------------------------------------------------------------------
# Theme
# --------------------------------------------------------------------------

def apply_theme():
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        html, body, .stApp { background: #ffffff; color: #16233a; }
        .stAppViewContainer .main .block-container {
            max-width: 980px !important; padding: 1rem 1.25rem 4rem !important; margin: 0 auto !important;
        }
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }

        /* ---- brand strip ---- */
        .dashboard-brand { display:flex; align-items:baseline; gap:10px; margin: 2px 0 14px; }
        .dashboard-brand .mark { color:#0f766e; font-size:15px; font-weight:800; letter-spacing:0.02em; }
        .dashboard-brand .team { color:#64748b; font-size:13px; }

        /* ---- hero ---- */
        .dash-hero { background: #ffffff; border: 1px solid #e1e7ef; border-radius: 14px;
            padding: 26px 28px; margin: 0 0 22px; box-shadow: 0 1px 3px rgba(15,23,42,0.05); }
        .dash-hero .eyebrow { color:#0f766e; font-size:12.5px; font-weight:700; margin:0 0 8px; }
        .dash-hero h1 { color:#0f172a; margin: 0 0 8px; font-size: 26px; font-weight: 750; line-height:1.28; }
        .dash-hero p { color:#475569; margin: 0; line-height: 1.55; font-size:14.5px; max-width: 640px; }
        .dash-hero .analyst { color:#0e7490; margin-top:10px; font-size:12px; }

        /* ---- segmented control tabs ---- */
        [data-testid="stSegmentedControl"] { width: 100%; background: #dbe4ee; border-radius: 12px; padding: 5px; margin-bottom: 18px; }
        [data-testid="stSegmentedControl"] button { flex: 1 1 0; min-height: 48px; padding: 9px 12px; border-radius: 8px;
            background: transparent; color: #334155; font-size: 13.5px; font-weight: 700; }
        [data-testid="stSegmentedControl"] button[aria-checked="true"], [data-testid="stSegmentedControl"] button[aria-pressed="true"] {
            background: #ccfbf1; color: #115e59; }

        /* ---- ONE card format for every section: this is the only white-box rule ---- */
        [data-testid="stVerticalBlockBorderWrapper"] {
            width: 100% !important; max-width: 100% !important;
            background: #ffffff !important; border: 1px solid #e1e7ef; border-radius: 12px;
            padding: 20px 22px 16px; margin: 0 0 16px !important;
            box-shadow: 0 1px 3px rgba(15,23,42,0.05);
        }
        [data-testid="stLayoutWrapper"] { background: #ffffff !important; }
        /* kill nested card styling so charts/etc inside a section don't create a second box */
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
            border: none; box-shadow: none; padding: 0; margin: 10px 0 0 !important; border-radius: 0;
        }

        .sec-title { color:#0f172a; font-size: 17.5px; font-weight: 750; margin: 0 0 4px; }
        .sec-subtext { color:#64748b; font-size: 13.5px; line-height: 1.5; margin: 0 0 12px; }
        .sec-takeaway { background: #ecfeff; border-left: 3px solid #0891b2; color: #0e5c68;
            padding: 9px 12px; border-radius: 0 8px 8px 0; margin: 0 0 14px; font-size: 13.5px; font-weight: 600; }
        .sec-explain { color:#475569; font-size: 16px; line-height:1.5; margin: 14px 0 4px;
            padding-top: 12px; border-top: 1px solid #eef2f7; }
        .sec-explain strong { color:#0f172a; }
        .sec-caption { color:#94a3b8; font-size: 11.5px; margin-top: 4px; }
        [data-testid="stExpander"], [data-testid="stExpander"] details { background: transparent !important;
            border: none !important; margin: 10px 0 0 !important; max-width: fit-content !important; }
        [data-testid="stExpander"] summary { color:#0f172a !important; font-size:10px !important;
            font-weight:600; line-height:1.2; padding:0 !important; min-height:0 !important; }
        [data-testid="stExpander"] summary:hover { color:#0f172a !important; text-decoration:none !important; }
        [data-testid="stExpander"] summary svg { color:#0f172a !important; }
        [data-testid="stExpander"] details[open] summary { margin-bottom: 8px; }
        .decision { background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706; color: #78350f;
            padding: 16px 18px; border-radius: 10px; margin: 4px 0 16px; line-height: 1.6; font-size: 14px; }
        .decision strong { color:#78350f; }

        [data-testid="stMetric"] { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; }
        [data-testid="stMetricValue"] { font-size: 22px; }

        /* ---- introduction ---- */
        .intro-hero { background: #ffffff; border: 1px solid #dbe4ee; border-left: 5px solid #0f766e; border-radius: 12px;
            padding: 26px 30px 22px; margin: 0 0 18px; box-shadow: 0 2px 8px rgba(15,23,42,0.04); }
        .intro-kicker, .intro-section-label { color: #0f766e; font-size: 11px; font-weight: 800; letter-spacing: 0.12em; }
        .intro-kicker { margin-bottom: 10px; }
        .intro-hero h1 { color: #0f172a; font-size: 30px; line-height: 1.2; margin: 0 0 12px; }
        .intro-problem { color: #334155; font-size: 15px; line-height: 1.6; max-width: 800px; margin: 0 0 10px; }
        .intro-instruction { color: #64748b; font-size: 12.5px; margin: 0; }
        .intro-section-label { margin: 26px 0 10px; }
        .intro-flow-root { background: #f0fdfa; border: 1px solid #99f6e4; border-radius: 10px; color: #115e59;
            padding: 14px 18px; text-align: center; font-weight: 800; margin: 0 auto 10px; max-width: 520px; }
        .intro-flow-arrow { color: #94a3b8; text-align: center; font-size: 20px; line-height: 1; margin: 2px 0; }
        .intro-node { background: #ffffff; border: 1px solid #dbe4ee; border-left: 4px solid; border-radius: 9px;
            padding: 12px 15px; margin: 8px auto 4px; max-width: 760px; }
        .intro-node-title { color: #0f172a; font-weight: 750; font-size: 14px; }
        .intro-node-owner { color: #64748b; font-size: 12px; margin-top: 3px; }
        .intro-node-action [data-testid="stButton"] button { background: #ffffff; border: 1px solid #cbd5e1;
            color: #0f766e; font-size: 12px; font-weight: 700; }
        .intro-question-panel { background: #f8fafc; border: 1px solid #dbe4ee; border-radius: 9px;
            padding: 14px 18px; margin: 4px auto 12px; max-width: 760px; }
        .intro-question-panel h4 { color: #0f172a; margin: 0 0 4px; font-size: 15px; }
        .intro-owner { color: #64748b; font-size: 12px; margin: 0 0 9px; }
        .intro-questions { margin: 0; padding-left: 22px; color: #334155; }
        .intro-questions li { margin: 8px 0; line-height: 1.45; font-size: 13px; }
        .intro-q-number { color: #64748b; font-weight: 800; margin-right: 8px; }
        .intro-signal { background: #ecfeff; border-left: 4px solid #0891b2; border-radius: 0 8px 8px 0; color: #164e63;
            padding: 13px 16px; margin: 14px 0 4px; font-size: 13px; line-height: 1.6; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# The single section format used on every tab
# --------------------------------------------------------------------------

def section_card(title, subtext, render_body, explanation=None, source=None, analyst=None,
                  report_key=None, takeaway=None, key_suffix=""):
    """One white card: title, subtext, optional takeaway, chart/body, explanation, source."""
    with st.container(border=True):
        st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
        if subtext:
            st.markdown(f'<div class="sec-subtext">{subtext}</div>', unsafe_allow_html=True)
        if takeaway:
            st.markdown(f'<div class="sec-takeaway">{takeaway}</div>', unsafe_allow_html=True)

        render_body()

        def source_method():
            with st.expander("ⓘ Source & method", expanded=False):
                if source:
                    st.caption(f"Source / dataset: `{source}`")
                if analyst:
                    st.caption(f"Analysed by: {analyst}")
                if report_key and report_key in REPORTS:
                    report_owner, report_path = REPORTS[report_key]
                    st.caption(f"Analysis report: {report_owner}")
                    if os.path.exists(report_path):
                        with open(report_path, "rb") as report_file:
                            st.download_button(
                                "Download analysis report", report_file.read(),
                                file_name=os.path.basename(report_path), mime="application/pdf",
                                key=f"report-{report_key}-{key_suffix}",
                            )
                    else:
                        st.caption(f"Report path: `{report_path}`")

        if explanation and (source or analyst):
            st.markdown(f'<div class="sec-explain"><strong>What this shows:</strong> {explanation}</div>', unsafe_allow_html=True)
            source_method()
        elif explanation:
            st.markdown(f'<div class="sec-explain"><strong>What this shows:</strong> {explanation}</div>', unsafe_allow_html=True)
        elif source or analyst:
            source_method()


def page_header(eyebrow, title, subtitle, analyst="Team synthesis"):
    st.markdown(
        f'<div class="dash-hero"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>'
        f'<p>{subtitle}</p><p class="analyst">Analysed by {analyst} &nbsp;·&nbsp; delivered orders with a review, unless stated otherwise</p></div>',
        unsafe_allow_html=True,
    )


def render_intro_mind_map():
    category_nodes = []
    question_nodes = []
    for index, (category_name, category) in enumerate(INTRO_CATEGORIES.items()):
        node_id = f"category-{index}"
        category_nodes.append(
            f'<button class="category-node" data-target="{node_id}" '
            f'style="--node-color:{category["color"]}">'
            f'<span>{category_name}</span><small>{category["owner"]}</small></button>'
        )
        question_nodes.append(
            f'<div class="question-group" id="questions-{node_id}">'
            + "".join(
                f'<button class="question-node" style="--node-color:{category["color"]}">'
                f'{question}</button>'
                for question in category["questions"]
            )
            + "</div>"
        )

    mind_map_html = f"""
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; background: #ffffff; font-family: Georgia, 'Times New Roman', serif; color: #ffffff; }}
        .mind-map {{
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 900px;
            padding: 14px 6px 24px;
            overflow: hidden;
        }}
        .root-wrap {{ width: min(430px, 92%); position: relative; }}
        .root-wrap::after, .category-branch::after {{
            content: "";
            display: block;
            height: 24px;
            width: 2px;
            margin: 0 auto;
            background: #9db4ff;
        }}
        .root-node {{
            width: 100%;
            border: 0;
            border-radius: 6px;
            padding: 12px 14px;
            background: #596174;
            color: #ffffff;
            font-size: 14px;
            line-height: 1.25;
            text-align: center;
            cursor: pointer;
        }}
        .category-column {{ width: min(760px, 96%); }}
        .category-branch {{ position: relative; width: 100%; }}
        .category-node, .question-node {{ border: 0; border-radius: 6px; color: #ffffff;
            font-family: Georgia, 'Times New Roman', serif; text-align: left; cursor: pointer; }}
        .category-node {{
            display: block;
            width: min(430px, 82%);
            margin: 0 auto;
            background: var(--node-color);
            padding: 11px 13px;
            font-size: 14px;
            line-height: 1.2;
            box-shadow: 0 3px 8px rgba(15,23,42,0.12);
        }}
        .category-node:hover, .category-node.active {{ filter: brightness(0.92); }}
        .category-node small {{ display: block; color: rgba(255,255,255,0.84); font-family: Arial, sans-serif; font-size: 10px; margin-top: 4px; }}
        .question-group {{
            width: min(620px, 92%);
            margin: 0 auto;
            display: flex;
            flex-direction: row;
            justify-content: center;
            gap: 12px;
            padding-top: 0;
        }}
        .question-group::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 50%;
            height: 14px;
            border-left: 2px solid #9db4ff;
        }}
        .question-node {{
            flex: 1;
            background: #304640;
            padding: 11px 14px;
            font-size: 13px;
            line-height: 1.25;
            border-top: 3px solid var(--node-color);
            margin-top: 14px;
        }}
        .question-node:hover {{ background: #3b5b50; }}
        .question-group.is-hidden {{ display: none; }}
        @media (max-width: 760px) {{
            .mind-map {{ min-height: 1100px; padding-left: 0; padding-right: 0; }}
            .root-node {{ font-size: 11px; padding: 9px; }}
            .category-node {{ font-size: 11px; padding: 9px 7px; }}
            .category-node small {{ font-size: 8px; }}
            .question-node {{ font-size: 10px; padding: 8px; }}
            .question-group {{ flex-direction: column; gap: 6px; }}
            .question-node {{ margin-top: 14px; }}
        }}
    </style>
    <div class="mind-map">
        <div class="root-wrap">
            <button class="root-node" id="root-node">Marketplace Growth and Customer Trust</button>
        </div>
        <div class="category-column">
            {"".join(
                f'<div class="category-branch">{category_node}{question_node}</div>'
                for category_node, question_node in zip(category_nodes, question_nodes)
            )}
        </div>
    </div>
    <script>
        const categoryNodes = document.querySelectorAll('.category-node');
        categoryNodes.forEach((node) => {{
            node.addEventListener('click', () => {{
                const target = document.getElementById('questions-' + node.dataset.target);
                const hidden = target.classList.toggle('is-hidden');
                node.classList.toggle('active', !hidden);
            }});
        }});
        document.getElementById('root-node').addEventListener('click', () => {{
            document.querySelectorAll('.question-group').forEach((group) => group.classList.remove('is-hidden'));
            document.querySelectorAll('.category-node').forEach((node) => node.classList.remove('active'));
        }});
    </script>
    """
    components.html(mind_map_html, height=505, scrolling=False)


def render_mermaid_mind_map():
    mermaid_definition = r'''
flowchart TD
    P["MARKETPLACE GROWTH & CUSTOMER TRUST<br/>Grow sales without breaking customer trust"]

    P --> D["DELIVERY PERFORMANCE<br/>Yash Arabhavi"]
    D --> DQ1["Q1: How strongly does delivery lateness predict a bad review,<br/>and where is the cliff edge?"]
    D --> DQ2["Q2: Is it being slow or breaking the promise<br/>that angers customers more?"]

    D --> R["REGIONAL LOGISTICS<br/>Anushka"]
    R --> RQ1["Q1: Do certain regions experience systematically<br/>worse delivery performance and satisfaction?"]
    R --> RQ2["Q2: Which seller-state to customer-state<br/>routes perform worst?"]

    R --> S["SELLER PERFORMANCE<br/>Kannan S"]
    S --> SQ1["Q1: How concentrated is the damage across sellers,<br/>especially the worst 5%?"]
    S --> SQ2["Q2: Are certain sellers a recurring source of bad experiences<br/>regardless of category or delivery time?"]

    S --> B["SELLER BEHAVIOUR DRIVERS<br/>Sahib Randhawa"]
    B --> BQ1["Q1: Which seller behaviours predict bad reviews:<br/>handling time, order volume, catalogue breadth, or freight pricing?"]
    B --> BQ2["Q2: Where should the company invest in logistics,<br/>sellers, or regions to grow while preserving satisfaction?"]

    B --> PP["PRODUCT & PRICING<br/>Ashwanth V"]
    PP --> PPQ1["Q1: Beyond delivery, what else moves the score:<br/>price, freight ratio, product weight and size,<br/>photo count, description length, or number of items?"]
    PP --> PPQ2["Q2: Which product categories carry high revenue<br/>and poor satisfaction?"]

    style P fill:#111827,color:#ffffff,stroke:#111827,stroke-width:3px
    style D fill:#0891b2,color:#ffffff,stroke:#0891b2,stroke-width:2px
    style DQ1 fill:#ecfeff,color:#164e63,stroke:#0891b2
    style DQ2 fill:#ecfeff,color:#164e63,stroke:#0891b2
    style R fill:#2563eb,color:#ffffff,stroke:#2563eb,stroke-width:2px
    style RQ1 fill:#eff6ff,color:#1e3a8a,stroke:#2563eb
    style RQ2 fill:#eff6ff,color:#1e3a8a,stroke:#2563eb
    style S fill:#059669,color:#ffffff,stroke:#059669,stroke-width:2px
    style SQ1 fill:#ecfdf5,color:#064e3b,stroke:#059669
    style SQ2 fill:#ecfdf5,color:#064e3b,stroke:#059669
    style B fill:#d97706,color:#ffffff,stroke:#d97706,stroke-width:2px
    style BQ1 fill:#fffbeb,color:#78350f,stroke:#d97706
    style BQ2 fill:#fffbeb,color:#78350f,stroke:#d97706
    style PP fill:#db2777,color:#ffffff,stroke:#db2777,stroke-width:2px
    style PPQ1 fill:#fdf2f8,color:#831843,stroke:#db2777
    style PPQ2 fill:#fdf2f8,color:#831843,stroke:#db2777

    linkStyle 0 stroke:#6b7280,stroke-width:3px
    linkStyle 3 stroke:#6b7280,stroke-width:2px
    linkStyle 6 stroke:#6b7280,stroke-width:2px
    linkStyle 9 stroke:#6b7280,stroke-width:2px
    linkStyle 12 stroke:#6b7280,stroke-width:2px
    linkStyle 1,2 stroke:#0891b2,stroke-width:2px
    linkStyle 4,5 stroke:#2563eb,stroke-width:2px
    linkStyle 7,8 stroke:#059669,stroke-width:2px
    linkStyle 10,11 stroke:#d97706,stroke-width:2px
    linkStyle 13,14 stroke:#db2777,stroke-width:2px
'''
    mermaid_html = f'''
    <style>
        html, body {{ margin: 0; padding: 0; background: #ffffff; overflow: hidden; }}
        .mermaid {{ display: flex; justify-content: center; background: #ffffff; padding: 12px 12px 0; }}
        .mermaid svg {{ max-width: none; overflow: visible; }}
    </style>
    <div class="mermaid">{mermaid_definition}</div>
    <script type="module">
        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
        mermaid.initialize({{
            startOnLoad: true,
            securityLevel: "loose",
            theme: "base",
            flowchart: {{
                htmlLabels: true,
                nodeSpacing: 90,
                rankSpacing: 200,
                padding: 28,
            }},
            themeVariables: {{ fontFamily: "Georgia", fontSize: "20px" }}
        }});
    </script>
    '''
    components.html(mermaid_html, height=1000, scrolling=False)


def render_introduction(df):
    """Orient the reader around the business problem before the analytical story."""
    d = reviewed_delivered(df)
    if d.empty:
        st.warning("No reviewed delivered orders are available.")
        return

    st.markdown(
        '<div class="intro-hero">'
        '<h1>Can we grow without breaking customer trust?</h1>'
        '<p class="intro-problem"><strong>Problem statement:</strong> The marketplace is growing, but poor customer experiences can quietly erode repeat demand. '
        'We need to identify where dissatisfaction starts, how much is operationally avoidable, and where leadership should intervene first.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="intro-section-label">IMPORTANT DATA SIGNALS</div>', unsafe_allow_html=True)
    monthly = d.assign(Month=d["order_purchase_timestamp"].dt.to_period("M").astype(str)).groupby("Month").agg(
        Orders=("order_id", "count"),
        Negative_rate=("is_negative", "mean"),
        Unhappy_orders=("is_negative", "sum"),
        Late_rate=("is_late", "mean"),
        Revenue=("total_price", "sum"),
    ).reset_index()
    monthly["Unhappy customer rate"] = monthly.pop("Negative_rate") * 100
    monthly["Orders delivered late"] = monthly.pop("Late_rate") * 100
    monthly["Revenue (R$)"] = monthly.pop("Revenue")
    monthly = monthly[monthly["Orders"] >= 100]
    overall_unhappy_rate = d["is_negative"].mean() * 100
    late = d[d["is_late"] == True]
    on_time = d[d["is_late"] == False]
    on_time_unhappy = on_time["is_negative"].mean() * 100
    late_unhappy = late["is_negative"].mean() * 100
    date_start = d["order_purchase_timestamp"].min().strftime("%b %Y")
    date_end = d["order_purchase_timestamp"].max().strftime("%b %Y")
    c1, c2, c3 = st.columns(3)
    c1.metric("Analysis period", f"{date_start} - {date_end}")
    c2.metric("Reviewed delivered orders", f"{len(d):,}")
    c3.metric("Unhappy customer rate", f"{overall_unhappy_rate:.1f}%", help="Share of reviewed orders rated 1 or 2 stars")

    c1, c2, c3 = st.columns(3)
    c1.metric("Late-order dissatisfaction impact", f"{late_unhappy / on_time_unhappy:.1f}x", help="Unhappy-review rate when late divided by the unhappy-review rate when on time")
    c2.metric("Unhappy when delivered on time", f"{on_time_unhappy:.1f}%")
    c3.metric("Unhappy when delivered late", f"{late_unhappy:.1f}%")

    st.markdown("**Customer dissatisfaction and revenue trend**")
    dissatisfaction_bars = alt.Chart(monthly).mark_bar(color="#e11d48", opacity=0.82).encode(
        x=alt.X("Month:O", title="Month"),
        y=alt.Y("Unhappy customer rate:Q", title="Unhappy customers (%)", scale=alt.Scale(zero=True)),
        tooltip=[
            alt.Tooltip("Month:O", title="Month"),
            alt.Tooltip("Unhappy customer rate:Q", title="Unhappy customers (1-2 stars)", format=".1f"),
            alt.Tooltip("Unhappy_orders:Q", title="Unhappy reviews", format=",.0f"),
            alt.Tooltip("Orders:Q", title="Reviewed orders", format=",.0f"),
        ],
    )
    revenue_line = alt.Chart(monthly).mark_line(point=True, color="#059669", strokeWidth=3).encode(
        x=alt.X("Month:O", title="Month"),
        y=alt.Y("Revenue (R$):Q", title="Revenue (R$)", axis=alt.Axis(orient="right"), scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("Month:O", title="Month"),
            alt.Tooltip("Revenue (R$):Q", title="Revenue", format=",.0f"),
            alt.Tooltip("Orders:Q", title="Reviewed orders", format=",.0f"),
        ],
    )
    st.markdown(
        '<div style="display:flex;gap:22px;align-items:center;margin:2px 0 6px;color:#475569;font-size:12px;">'
        '<span><span style="display:inline-block;width:10px;height:10px;background:#e11d48;margin-right:6px;"></span>Customer dissatisfaction: 1-2 star reviews</span>'
        '<span><span style="display:inline-block;width:10px;height:3px;background:#059669;margin-right:6px;vertical-align:middle;"></span>Revenue</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    show(
        alt.layer(dissatisfaction_bars, revenue_line)
        .resolve_scale(y="independent")
        .properties(height=360)
    )
    st.caption(
        "The left axis shows the percentage of reviewed orders rated 1-2 stars; the right axis shows monthly revenue. "
        "This keeps the two measures visible together without treating percentage and currency as the same scale."
    )
    if len(monthly) >= 2:
        first_month = monthly.iloc[0]
        latest_month = monthly.iloc[-1]
        revenue_change = (latest_month["Revenue (R$)"] / first_month["Revenue (R$)"] - 1) * 100
        dissatisfaction_change = latest_month["Unhappy customer rate"] - first_month["Unhappy customer rate"]
        trend_relationship = "moved in the same direction" if revenue_change * dissatisfaction_change >= 0 else "moved in opposite directions"
        st.markdown(
            f'<div class="intro-signal"><strong>Trend:</strong> from {first_month["Month"]} to {latest_month["Month"]}, '
            f'revenue changed by {revenue_change:+.1f}% while the share of unhappy customers changed by '
            f'{dissatisfaction_change:+.1f} percentage points. The two measures {trend_relationship}; '
            'this describes the pattern in the data, not a causal effect.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="intro-section-label">THE INVESTIGATION FLOW</div>', unsafe_allow_html=True)
    render_mermaid_mind_map()


# --------------------------------------------------------------------------
# Chart builders — return alt.Chart objects, never render directly
# --------------------------------------------------------------------------

def bar_chart_obj(frame, x, y, color="#2563eb", sort="-y"):
    return alt.Chart(frame).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(f"{x}:N", sort=sort, title=None),
        y=alt.Y(f"{y}:Q", title=None),
        color=alt.value(color),
        tooltip=[alt.Tooltip(f"{x}:N", title=x), alt.Tooltip(f"{y}:Q", title=y, format=".1f")],
    ).properties(height=340)


def line_chart_obj(frame, x, y_columns, colors=None):
    values = frame.melt(id_vars=[x], value_vars=y_columns, var_name="Metric", value_name="Value")
    return alt.Chart(values).mark_line(point=True).encode(
        x=alt.X(f"{x}:O", title=None),
        y=alt.Y("Value:Q", title=None),
        color=alt.Color("Metric:N", scale=alt.Scale(range=colors or ["#0891b2", "#e11d48"])),
        tooltip=[alt.Tooltip(f"{x}:O", title=x), alt.Tooltip("Metric:N"), alt.Tooltip("Value:Q", format=".1f")],
    ).properties(height=340)


def show(chart):
    st.altair_chart(chart, use_container_width=True)


# --------------------------------------------------------------------------
# Tab 1 — Trust & Growth (overview)
# --------------------------------------------------------------------------

def render_overview(df):
    page_header(
        "Executive overview",
        "Can We Grow Without Breaking Customer Trust?",
        "Where can we grow sales, and where must we intervene before customer satisfaction deteriorates?",
    )
    d = reviewed_delivered(df)
    if d.empty:
        st.warning("No reviewed delivered orders are available.")
        return

    baseline = d["is_negative"].mean() * 100
    late = d[d["is_late"] == True]
    on_time = d[d["is_late"] == False]
    late_share = len(late) / len(d) * 100
    negative_share = late["is_negative"].sum() / d["is_negative"].sum() * 100 if d["is_negative"].sum() else 0

    # Section 1 — KPI snapshot
    def kpis():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Reviewed orders", f"{len(d):,}")
        c2.metric("Negative rate", f"{baseline:.1f}%")
        c3.metric("Late share", f"{late_share:.1f}%")
        c4.metric("Late negative rate", f"{late['is_negative'].mean() * 100:.1f}%" if len(late) else "n/a")

    section_card(
        "At a glance", "The baseline every other page compares against.", kpis,
        explanation="Reviewed, delivered orders across the full study period, with the two headline rates leadership tracks.",
        source="processed_data/master_orders.csv", analyst="Team synthesis", key_suffix="overview-kpi",
    )

    # Section 2 — the twist
    risk = pd.DataFrame({
        "Group": ["On time", "Late"],
        "Negative rate": [on_time["is_negative"].mean() * 100, late["is_negative"].mean() * 100 if len(late) else 0],
    })
    section_card(
        "Risk summary",
        "Late delivery is a small share of orders but a much larger share of negative reviews.",
        lambda: show(bar_chart_obj(risk, "Group", "Negative rate", "#0891b2")),
        explanation="Late delivery creates a much larger negative-review rate than its share of orders alone would suggest.",
        source="processed_data/master_orders.csv", analyst="Team synthesis",
        takeaway=f"Late orders are {late_share:.1f}% of deliveries. They produce {negative_share:.1f}% of all negative reviews.",
        key_suffix="overview-risk",
    )

    # Section 3 — growth vs experience
    category = rate_table(d, "primary_category", "Category").sort_values("GMV", ascending=False).head(15)
    category["Risk"] = np.where(category["Negative rate"] > baseline, "Above baseline", "Below baseline")

    def cat_scatter():
        chart = alt.Chart(category).mark_circle(opacity=0.85).encode(
            x=alt.X("GMV:Q", title="Category GMV (R$)"),
            y=alt.Y("Negative rate:Q", title="Negative-review rate (%)"),
            size=alt.Size("Orders:Q", title="Reviewed orders"),
            color=alt.Color("Risk:N", scale=alt.Scale(domain=["Above baseline", "Below baseline"], range=["#e11d48", "#059669"])),
            tooltip=["Category:N", "Orders:Q", "GMV:Q", "Negative rate:Q"],
        ).properties(height=380)
        show(chart)

    section_card(
        "Growth versus experience",
        "Categories with material GMV and above-baseline negative rates are the clearest intervention zone.",
        cat_scatter,
        explanation="High-GMV categories above the baseline are where growth investment and customer risk overlap.",
        source="processed_data/master_orders.csv + processed_data/order_items.csv",
        analyst="Ashwanth V / Team synthesis", report_key="Product portfolio", key_suffix="overview-category",
    )

    # Section 4 — monthly trend
    monthly = d.assign(Month=d["order_purchase_timestamp"].dt.to_period("M").astype(str)).groupby("Month").agg(
        Negative_rate=("is_negative", "mean"), Late_rate=("is_late", "mean")
    ) * 100
    section_card(
        "Monthly context",
        "Negative-review rate and late-delivery rate, tracked together over time.",
        lambda: st.line_chart(numeric_chart(monthly, ["Negative_rate", "Late_rate"])),
        explanation="The two rates move together (r = 0.80), reinforcing that delivery execution is the driver, not seasonal noise.",
        source="processed_data/master_orders.csv", analyst="Team synthesis", key_suffix="overview-monthly",
    )

    st.markdown(
        '<div class="decision"><strong>Leadership signal:</strong> protect the promise date first, '
        'then target the sellers, routes, and categories where risk and commercial exposure overlap.</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Tab 2 — Promise vs Speed
# --------------------------------------------------------------------------

def render_delivery(df):
    page_header(
        "Delivery promise", "Missing the Promise Is a Cliff, Not a Slope",
        "95,824 delivered and reviewed orders · two questions: how does delay affect reviews, and is it slowness or a broken promise that angers customers?",
        "Yash Arabhavi",
    )
    d = reviewed_delivered(df)
    on_time = d[d["is_late"] == False]
    late = d[d["is_late"] == True]
    baseline = d["is_negative"].mean() * 100

    # ── Chart 1 — delay buckets (full row, 14 bars) ─────────────────────────
    delay_buckets = pd.DataFrame({
        "Bucket": ["30+ e", "15–30 e", "7–15 e", "3–7 e", "0–3 e",
                   "1d", "2d", "3d", "4–5d", "6–7d", "8–10d", "11–15d", "16–30d", "30+d"],
        "Neg %":  [10.8, 8.9, 8.9, 10.3, 11.6,
                   19.6, 34.3, 50.4, 60.2, 74.7, 80.3, 79.5, 82.1, 67.8],
        "CI lo":  [9.7, 8.6, 8.6, 9.7, 10.7,
                   17.1, 30.4, 46.0, 56.9, 71.7, 77.3, 76.7, 79.4, 62.6],
        "CI hi":  [12.0, 9.2, 9.2, 10.9, 12.6,
                   22.5, 38.4, 54.8, 63.4, 77.5, 83.0, 82.1, 84.6, 72.6],
        "n":      [2712, 32059, 40973, 9429, 4270,
                   820, 536, 496, 870, 878, 756, 845, 851, 329],
        "Side":   ["On time"] * 5 + ["Late"] * 9,
    })
    bucket_order = delay_buckets["Bucket"].tolist()

    baseline_rule = alt.Chart(pd.DataFrame({"y": [baseline]})).mark_rule(
        color="#64748b", strokeDash=[4, 3], strokeWidth=1.5,
    ).encode(y=alt.Y("y:Q"))

    chart1_bars = alt.Chart(delay_buckets).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("Bucket:N", sort=bucket_order, title="Days vs promised date (early ←  |  → late)",
                axis=alt.Axis(labelFontSize=12, titleFontSize=13, labelPadding=6)),
        y=alt.Y("Neg %:Q", title="Negative-review rate (%)", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        color=alt.Color("Side:N", scale=alt.Scale(
            domain=["On time", "Late"], range=["#2563eb", "#e11d48"]
        ), legend=alt.Legend(title="Delivery status", orient="bottom", direction="horizontal",
                             titleFontSize=12, labelFontSize=12, padding=8)),
        tooltip=[
            alt.Tooltip("Bucket:N", title="Bucket"),
            alt.Tooltip("Side:N", title="Status"),
            alt.Tooltip("Neg %:Q", title="Negative rate", format=".1f"),
            alt.Tooltip("n:Q", title="Orders", format=","),
            alt.Tooltip("CI lo:Q", title="CI low", format=".1f"),
            alt.Tooltip("CI hi:Q", title="CI high", format=".1f"),
        ],
    )
    chart1_errors = alt.Chart(delay_buckets).mark_errorbar(color="#475569", ticks=True).encode(
        x=alt.X("Bucket:N", sort=bucket_order),
        y=alt.Y("CI lo:Q", title=""),
        y2=alt.Y2("CI hi:Q"),
    )
    chart1 = (chart1_bars + chart1_errors + baseline_rule).properties(
        height=450,
        title=alt.TitleParams(
            "Bad-review rate by how early or late the order arrived",
            subtitle="95% Wilson CI error bars · dashed line = platform baseline · blue = early/on-time · red = late",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b",
            anchor="start", dy=-4,
        ),
    )

    def chart1_body():
        show(chart1)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            '95,824 delivered &amp; reviewed orders. Early buckets run 8.9–11.6%; one day late jumps to 19.6%; three days late reaches 50.4%.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q1 · How does delivery delay affect reviews?",
        None,
        chart1_body,
        takeaway=(
            f"On-time: {on_time['is_negative'].mean() * 100:.1f}% negative · "
            f"Late: {late['is_negative'].mean() * 100:.1f}% negative — {late['is_negative'].mean() / on_time['is_negative'].mean():.1f}× worse. "
            f"Late deliveries are {len(late)/len(d)*100:.1f}% of orders but cause 32.5% of all bad reviews."
        ),
        source="analysis/Yash/outputs/q1_delay_buckets.csv",
        analyst="Yash Arabhavi", report_key="Delivery promise", key_suffix="delivery-q1",
    )

    # ── Chart 2 — never-arrived orders (full row, horizontal) ───────────────
    excluded = pd.DataFrame({
        "Group": [
            "delivered, on time", "delivered, late",
            "shipped, never arrived", "canceled, never arrived",
            "invoiced, never arrived", "unavailable, never arrived",
            "processing, never arrived",
        ],
        "Neg %": [9.2, 62.3, 69.3, 76.7, 81.9, 84.7, 92.5],
        "n":     [89443, 6381, 1032, 605, 309, 595, 295],
        "Type":  ["In analysis", "In analysis",
                  "Excluded — never arrived", "Excluded — never arrived",
                  "Excluded — never arrived", "Excluded — never arrived",
                  "Excluded — never arrived"],
    }).sort_values("Neg %")

    chart2 = alt.Chart(excluded).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
        y=alt.Y("Group:N", sort=alt.EncodingSortField("Neg %", order="ascending"), title=None,
                axis=alt.Axis(labelFontSize=13, labelLimit=260)),
        x=alt.X("Neg %:Q", title="Negative-review rate (%)", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        color=alt.Color("Type:N", scale=alt.Scale(
            domain=["In analysis", "Excluded — never arrived"],
            range=["#2563eb", "#e11d48"],
        ), legend=alt.Legend(title=None, orient="bottom", direction="horizontal",
                             labelFontSize=12, padding=8)),
        tooltip=[
            alt.Tooltip("Group:N", title="Group"),
            alt.Tooltip("Neg %:Q", title="Negative rate", format=".1f"),
            alt.Tooltip("n:Q", title="Orders", format=","),
            alt.Tooltip("Type:N", title="Category"),
        ],
    ).properties(
        height=400,
        title=alt.TitleParams(
            "The angriest customers are the ones the delay analysis cannot see",
            subtitle="Orders that never arrived are excluded from the delay analysis but shown here for context",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b",
            anchor="start", dy=-4,
        ),
    )

    def chart2_body():
        show(chart2)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            '2,849 orders that never arrived average 78% negative — worse than any delivered-late group and invisible to Q1.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q1 · The hidden worst case",
        None,
        chart2_body,
        source="analysis/Yash/outputs/q1_excluded_orders.csv",
        analyst="Yash Arabhavi", report_key="Delivery promise", key_suffix="delivery-excluded",
    )

    # ── Chart 3 — two slopes on shared y scale (full row) ───────────────────
    speed_on_time = pd.DataFrame({
        "Bucket": ["≤7d", "8–14d", "15–21d", "22–30d", "31–45d", "45d+"],
        "Neg %":  [7.4, 8.7, 10.6, 14.4, 21.2, 33.3],
        "CI lo":  [7.1, 8.5, 10.2, 13.5, 18.7, 21.4],
        "CI hi":  [7.7, 9.0, 11.1, 15.3, 24.0, 47.9],
        "n":      [25875, 39684, 17056, 5873, 910, 45],
        "Series": ["Promise KEPT — cost of a longer wait"] * 6,
    })
    lateness = pd.DataFrame({
        "Bucket": ["1–2d late", "3–5d late", "6–10d late", "11–20d late", "21–40d late", "40d+ late"],
        "Neg %":  [25.4, 56.7, 77.3, 80.0, 82.7, 57.3],
        "CI lo":  [23.2, 54.0, 75.2, 77.7, 79.4, 50.1],
        "CI hi":  [27.8, 59.3, 79.3, 82.1, 85.6, 64.2],
        "n":      [1356, 1366, 1634, 1261, 579, 185],
        "Series": ["Promise BROKEN — cost of being later"] * 6,
    })
    two_slopes = pd.concat([speed_on_time, lateness], ignore_index=True)

    chart3_lines = alt.Chart(two_slopes).mark_line(point=alt.OverlayMarkDef(size=80), strokeWidth=2.5).encode(
        x=alt.X("Bucket:N", sort=None, title="Duration bucket",
                axis=alt.Axis(labelFontSize=12, titleFontSize=13, labelPadding=6)),
        y=alt.Y("Neg %:Q", title="Negative-review rate (%)", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        color=alt.Color("Series:N", scale=alt.Scale(
            domain=["Promise KEPT — cost of a longer wait", "Promise BROKEN — cost of being later"],
            range=["#2563eb", "#e11d48"],
        ), legend=alt.Legend(title=None, orient="bottom", direction="horizontal",
                             labelFontSize=12, padding=10)),
        tooltip=[
            alt.Tooltip("Series:N", title="Series"),
            alt.Tooltip("Bucket:N", title="Bucket"),
            alt.Tooltip("Neg %:Q", title="Negative rate", format=".1f"),
            alt.Tooltip("n:Q", title="Orders", format=","),
        ],
    )
    chart3_errors = alt.Chart(two_slopes).mark_errorbar(ticks=True).encode(
        x=alt.X("Bucket:N", sort=None),
        y=alt.Y("CI lo:Q"),
        y2=alt.Y2("CI hi:Q"),
        color=alt.Color("Series:N", scale=alt.Scale(
            domain=["Promise KEPT — cost of a longer wait", "Promise BROKEN — cost of being later"],
            range=["#2563eb", "#e11d48"],
        ), legend=None),
    )
    chart3 = (chart3_lines + chart3_errors).properties(
        height=450,
        title=alt.TitleParams(
            "Being slow costs points. Breaking the promise costs the customer.",
            subtitle="Same y-axis on both series — a 14-point rise does not look like a 57-point one",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b",
            anchor="start", dy=-4,
        ),
    )

    def chart3_body():
        show(chart3)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            'Promise kept: 7.4% → 21.2% across delivery durations (14 pp range). '
            'Promise broken: 25.4% → 82.7% across lateness buckets (57 pp range) — 4.2× wider. '
            'A month-long on-time wait (21.2%) still beats missing the date by 1–2 days (25.4%).'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q2 · Slowness or a broken promise?",
        None,
        chart3_body,
        takeaway="Breaking the promise is clearly worse. A month-long on-time wait (21.2% negative) is still better than missing the date by 1–2 days (25.4%).",
        source="analysis/Yash/outputs/q2_speed_on_time.csv · analysis/Yash/outputs/q2_lateness.csv",
        analyst="Yash Arabhavi", report_key="Delivery promise", key_suffix="delivery-q2",
    )

    # ── Chart 4 — review timing stacked bar (full row) ──────────────────────
    timing = pd.DataFrame({
        "Group": ["Promise kept (on time)", "Promise kept (on time)",
                  "Promise broken (late)", "Promise broken (late)"],
        "Timing": ["Reviewed after it arrived", "Reviewed before it arrived",
                   "Reviewed after it arrived", "Reviewed before it arrived"],
        "Share": [99.7, 0.3, 25.5, 74.5],
    })
    chart4 = alt.Chart(timing).mark_bar().encode(
        y=alt.Y("Group:N", title=None,
                scale=alt.Scale(paddingInner=0.4),
                axis=alt.Axis(labelFontSize=14, labelLimit=300, labelPadding=10)),
        x=alt.X("Share:Q", title="Share of orders (%)", scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        color=alt.Color("Timing:N", scale=alt.Scale(
            domain=["Reviewed after it arrived", "Reviewed before it arrived"],
            range=["#2563eb", "#e11d48"],
        ), legend=alt.Legend(title="Survey timing", orient="bottom", direction="horizontal",
                             titleFontSize=12, labelFontSize=12, padding=10)),
        order=alt.Order("Timing:N", sort="descending"),
        tooltip=[
            alt.Tooltip("Group:N", title="Group"),
            alt.Tooltip("Timing:N", title="Survey timing"),
            alt.Tooltip("Share:Q", title="Share (%)", format=".1f"),
        ],
    ).properties(
        height=240,
        title=alt.TitleParams(
            "Late customers rate a parcel they do not have yet",
            subtitle="Survey goes out on delivery, or on the promised date if nothing arrived — whichever comes first",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b",
            anchor="start", dy=-4,
        ),
    )

    def chart4_body():
        show(chart4)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            'Promise kept (n=89,443): 99.7% reviewed after arrival, median 1 day after. '
            'Promise broken (n=6,381): 74.5% reviewed <em>before</em> their parcel arrived, median 4 days before. '
            'Three out of four late reviews are not about a late delivery — they are about an order that has not shown up yet.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q2 · When does the review survey go out?",
        None,
        chart4_body,
        source="analysis/Yash/outputs/q2_review_timing.csv",
        analyst="Yash Arabhavi", report_key="Delivery promise", key_suffix="delivery-timing",
    )


# --------------------------------------------------------------------------
# Tab 3 — Multi-Seller Blind Spot
# --------------------------------------------------------------------------

def render_multi_seller(df):
    page_header(
        "Data-quality finding", "Why Do Multi-Seller Orders Look On-Time but Feel Bad?",
        "Multi-seller orders may look on-time at order level while the customer still experiences a fragmented delivery.",
    )
    d = reviewed_delivered(df)

    comparison = d.groupby("is_multi_seller").agg(
        Orders=("order_id", "count"), Late_rate=("is_late", "mean"), Negative_rate=("is_negative", "mean"), GMV=("total_price", "sum")
    ).reset_index()
    comparison["Order type"] = comparison["is_multi_seller"].map({False: "Single-seller", True: "Multi-seller"})
    comparison["Late rate"] = (comparison.pop("Late_rate") * 100).round(1)
    comparison["Negative rate"] = (comparison.pop("Negative_rate") * 100).round(1)
    comparison["GMV (R$)"] = comparison.pop("GMV").round(0)

    def gap_body():
        chart_df = comparison.melt(id_vars=["Order type", "Orders"], value_vars=["Late rate", "Negative rate"], var_name="Metric", value_name="Rate")
        chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X("Order type:N", title=None), y=alt.Y("Rate:Q", title="Rate (%)"),
            color=alt.Color("Metric:N", scale=alt.Scale(range=["#0891b2", "#e11d48"])),
            xOffset="Metric:N", tooltip=["Order type:N", "Orders:Q", "Metric:N", "Rate:Q"],
        ).properties(height=360)
        show(chart)

    section_card(
        "The multi-seller blind spot", "Recorded lateness versus actual customer dissatisfaction, by order type.", gap_body,
        explanation="A multi-seller order records one shipment event. The second-parcel theory is a hypothesis, not confirmed in the current data.",
        source="processed_data/master_orders.csv + processed_data/order_items_agg.csv", analyst="Team synthesis",
        takeaway="Multi-seller orders: 1.0% recorded late, 47.2% negative — a gap far larger than any single-seller segment shows.",
        key_suffix="multi-gap",
    )

    exposure = pd.DataFrame({
        "Metric": ["Order share", "GMV share", "Negative-review share"],
        "Share": [
            comparison.loc[comparison["Order type"] == "Multi-seller", "Orders"].iloc[0] / comparison["Orders"].sum() * 100,
            comparison.loc[comparison["Order type"] == "Multi-seller", "GMV (R$)"].iloc[0] / comparison["GMV (R$)"].sum() * 100,
            comparison.loc[comparison["Order type"] == "Multi-seller", "Negative rate"].iloc[0],
        ],
    })
    section_card(
        "How big is the blind spot",
        "Multi-seller share of orders, GMV, and negative reviews.",
        lambda: show(bar_chart_obj(exposure, "Metric", "Share", "#f59e0b")),
        explanation="Multi-seller orders represent a measurable share of marketplace exposure, so this blind spot can affect real commercial decisions.",
        source="processed_data/master_orders.csv + processed_data/order_items_agg.csv", analyst="Team synthesis",
        key_suffix="multi-exposure",
    )

    sellers = d.assign(Seller_count=pd.cut(d["n_sellers"], [-np.inf, 1, 2, np.inf], labels=["1 seller", "2 sellers", "3+ sellers"]))
    seller_count = rate_table(sellers, "Seller_count", "Seller count")
    section_card(
        "Negative rate by seller count",
        "Does the gap widen as more sellers are packed into one order?",
        lambda: show(bar_chart_obj(seller_count, "Seller count", "Negative rate", "#8b5cf6")),
        explanation="Negative experience should be monitored by seller count, since order-level attribution is incomplete for multi-seller orders.",
        source="processed_data/master_orders.csv + processed_data/order_items_agg.csv", analyst="Team synthesis",
        key_suffix="multi-count",
    )

    st.markdown(
        '<div class="decision"><strong>Recommendation:</strong> investigate seller-leg tracking for multi-seller orders, '
        'starting with a manual sample audit, before using their order-level late rate for performance decisions.</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Tab 4 — Seller Performance (Kannan S)
# --------------------------------------------------------------------------

def _build_seller_stats(df):
    """Build per-seller stats matching Kannan's notebook logic."""
    d = reviewed_delivered(df)

    # keep only single-seller orders
    if "n_sellers" in d.columns:
        single = d[d["n_sellers"] == 1].copy()
    else:
        single = d.copy()

    if single.empty or "primary_seller_id" not in single.columns:
        return single, pd.DataFrame(), pd.DataFrame(), 0.0

    bad_rate_platform = single["is_negative"].mean()

    # per-seller aggregation
    g = single.groupby("primary_seller_id")
    st_df = pd.DataFrame({
        "n_orders":  g.size(),
        "gmv":       g["total_price"].sum(),
        "n_bad":     g["is_negative"].sum(),
        "bad_rate":  g["is_negative"].mean(),
        "late_rate": g["is_late"].mean() if "is_late" in single.columns else pd.Series(0.0, index=g.size().index),
    }).reset_index().rename(columns={"primary_seller_id": "seller_id"})

    # simple expected rate (category-smoothed) if category available
    if "primary_category" in single.columns:
        cat_base = single.groupby("primary_category")["is_negative"].mean()
        single["p_expected"] = single["primary_category"].map(cat_base).fillna(bad_rate_platform)
    else:
        single["p_expected"] = bad_rate_platform

    if "is_late" in single.columns:
        band_base = single.groupby("is_late")["is_negative"].mean()
        single["p_expected"] = np.clip(
            single["p_expected"] * single["is_late"].map(band_base).fillna(bad_rate_platform) / (bad_rate_platform + 1e-9),
            0.005, 0.95,
        )

    exp = single.groupby("primary_seller_id")["p_expected"].sum().reset_index()
    exp.columns = ["seller_id", "expected_bad"]
    st_df = st_df.merge(exp, on="seller_id", how="left")
    st_df["expected_bad"] = st_df["expected_bad"].fillna(st_df["n_orders"] * bad_rate_platform)
    st_df["excess_bad"] = st_df["n_bad"] - st_df["expected_bad"]
    st_df["expected_bad_rate"] = st_df["expected_bad"] / st_df["n_orders"]

    # on-time bad rate
    if "is_late" in single.columns:
        ontime = single[single["is_late"] == False].groupby("primary_seller_id")["is_negative"].mean().reset_index()
        ontime.columns = ["seller_id", "bad_rate_ontime"]
        st_df = st_df.merge(ontime, on="seller_id", how="left")
    else:
        st_df["bad_rate_ontime"] = st_df["bad_rate"]

    qual = st_df[st_df["n_orders"] >= 10].copy()

    # z-score for offender detection
    eps = 1e-9
    qual["z"] = (
        (qual["n_bad"] - qual["expected_bad"])
        / np.sqrt(qual["n_orders"] * qual["expected_bad_rate"] * (1 - qual["expected_bad_rate"]) + eps)
    )
    qual["offender"] = (qual["z"] > 2) & (qual["bad_rate_ontime"] > bad_rate_platform)

    # failure mode
    late_mean = st_df["late_rate"].mean()
    qual["failure_mode"] = np.select(
        [
            (qual["late_rate"] > 2 * late_mean) & (qual["bad_rate_ontime"] > 2 * bad_rate_platform),
            qual["bad_rate_ontime"] > 2 * bad_rate_platform,
            qual["late_rate"] > 2 * late_mean,
        ],
        ["MIXED", "PRODUCT", "FULFILMENT"],
        default="BORDERLINE",
    )

    # delivery band for the band-level chart
    if "delay_days" in single.columns:
        single["band"] = pd.cut(
            single["delay_days"],
            [-np.inf, -10, -3, 0, 3, 10, np.inf],
            labels=["10+ d early", "3–10 d early", "0–3 d early", "0–3 d late", "3–10 d late", "10+ d late"],
        )
    else:
        single["band"] = "unknown"

    # merge offender flag back for band chart
    off_ids = set(qual.loc[qual["offender"], "seller_id"])
    single["group"] = np.where(single["primary_seller_id"].isin(off_ids), "Offenders", "Other sellers")

    return single, st_df, qual, bad_rate_platform


def render_sellers(df):
    page_header(
        "Seller performance", "Which Sellers Are a Recurring Source of Bad Experiences?",
        "77 sellers hold 11% of GMV but 53% of all avoidable damage — and they stay 2.4× worse even on parcels that arrived on time.",
        "Kannan S",
    )

    single, st_df, qual, BAD_RATE = _build_seller_stats(df)

    if qual.empty:
        st.warning("Seller data not available.")
        return

    off = qual[qual["offender"]]

    # ── EDA 1 + 2 — Review score distribution  |  Bad-review rate by delay band
    d = reviewed_delivered(df)
    rev_counts = d["review_score"].value_counts().sort_index().reset_index()
    rev_counts.columns = ["Score", "Orders"]
    rev_counts["Type"] = np.where(rev_counts["Score"] <= 2, "Bad (1–2 stars)", "Good (3–5 stars)")

    has_band = "delay_days" in single.columns and single["delay_days"].notna().any()
    if has_band:
        band_tbl = single.groupby("band", observed=True)["is_negative"].agg(
            Orders="size", bad_rate="mean"
        ).reset_index()
        band_tbl["bad_rate_pct"] = band_tbl["bad_rate"] * 100

    def eda12_body():
        c1, c2 = st.columns(2)
        with c1:
            chart1 = alt.Chart(rev_counts).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("Score:O", title="Review score", axis=alt.Axis(labelFontSize=13)),
                y=alt.Y("Orders:Q", title="Orders", axis=alt.Axis(labelFontSize=12)),
                color=alt.Color("Type:N", scale=alt.Scale(
                    domain=["Bad (1–2 stars)", "Good (3–5 stars)"], range=["#e11d48", "#2563eb"]
                ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
                tooltip=[alt.Tooltip("Score:O", title="Score"), alt.Tooltip("Orders:Q", title="Orders", format=",")],
            ).properties(
                height=320,
                title=alt.TitleParams(
                    "Reviews are U-shaped",
                    subtitle=f"Bad experience (1–2 ★) = {BAD_RATE:.1%} of orders",
                    fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                ),
            )
            show(chart1)
        with c2:
            if has_band:
                baseline_rule = alt.Chart(pd.DataFrame({"y": [BAD_RATE * 100]})).mark_rule(
                    color="#64748b", strokeDash=[4, 3], strokeWidth=1.5
                ).encode(y=alt.Y("y:Q"))
                bars2 = alt.Chart(band_tbl).mark_bar(
                    cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#2563eb"
                ).encode(
                    x=alt.X("band:N", sort=None, title="Delivery delay band",
                            axis=alt.Axis(labelFontSize=11, labelAngle=-20)),
                    y=alt.Y("bad_rate_pct:Q", title="Bad-review rate (%)", scale=alt.Scale(domain=[0, 100]),
                            axis=alt.Axis(labelFontSize=12)),
                    tooltip=[
                        alt.Tooltip("band:N", title="Band"),
                        alt.Tooltip("bad_rate_pct:Q", title="Bad-review rate (%)", format=".1f"),
                        alt.Tooltip("Orders:Q", title="Orders", format=","),
                    ],
                ).properties(
                    height=320,
                    title=alt.TitleParams(
                        "Late delivery is the strongest driver",
                        subtitle=f"Dashed = platform average {BAD_RATE:.1%}",
                        fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                    ),
                )
                show(bars2 + baseline_rule)

    section_card(
        "EDA · Review scores & delivery delay effect",
        None,
        eda12_body,
        source="processed_data/master_orders.csv",
        analyst="Kannan S", report_key="Seller performance", key_suffix="seller-eda12",
    )

    # ── EDA 3 + 4 — Category rates  |  Seller size concentration ────────────
    has_cat = "primary_category" in single.columns
    if has_cat:
        cat_tbl = (
            single[single["primary_category"].notna()]
            .groupby("primary_category")["is_negative"]
            .agg(Orders="size", bad_rate="mean")
            .query("Orders >= 200")
            .sort_values("bad_rate")
            .reset_index()
        )
        cat_tbl["bad_rate_pct"] = cat_tbl["bad_rate"] * 100
        n_show = min(8, len(cat_tbl) // 2)
        best = cat_tbl.head(n_show).assign(Group="Best")
        worst = cat_tbl.tail(n_show).assign(Group="Worst")
        cat_show = pd.concat([best, worst])
        cat_show["Category"] = cat_show["primary_category"].str.replace("_", " ")

    vol = st_df.sort_values("n_orders", ascending=False)["n_orders"]
    lorenz_x = np.arange(1, len(vol) + 1) / len(vol)
    lorenz_y = vol.cumsum().values / vol.sum()
    lorenz_df = pd.DataFrame({"Share of sellers (largest first)": lorenz_x, "Share of orders": lorenz_y})
    diagonal = pd.DataFrame({"Share of sellers (largest first)": [0.0, 1.0], "Share of orders": [0.0, 1.0]})
    top5_order_share = float(np.interp(0.05, lorenz_x, lorenz_y))

    def eda34_body():
        c1, c2 = st.columns(2)
        with c1:
            if has_cat:
                chart3 = alt.Chart(cat_show).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
                    y=alt.Y("Category:N", sort=alt.EncodingSortField("bad_rate_pct", order="ascending"),
                            title=None, axis=alt.Axis(labelFontSize=11, labelLimit=200)),
                    x=alt.X("bad_rate_pct:Q", title="Bad-review rate (%)", axis=alt.Axis(labelFontSize=11)),
                    color=alt.Color("Group:N", scale=alt.Scale(
                        domain=["Best", "Worst"], range=["#2563eb", "#e11d48"]
                    ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=11)),
                    tooltip=[
                        alt.Tooltip("Category:N", title="Category"),
                        alt.Tooltip("bad_rate_pct:Q", title="Bad-review rate (%)", format=".1f"),
                        alt.Tooltip("Orders:Q", title="Orders", format=","),
                    ],
                ).properties(
                    height=360,
                    title=alt.TitleParams(
                        "Category matters, but less than delivery",
                        subtitle=f"Best & worst categories (200+ orders) · avg {BAD_RATE:.1%}",
                        fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                    ),
                )
                show(chart3)
        with c2:
            curve_line = alt.Chart(lorenz_df).mark_line(color="#2563eb", strokeWidth=2).encode(
                x=alt.X("Share of sellers (largest first):Q", title="Share of sellers (largest first)",
                        axis=alt.Axis(format="%", labelFontSize=11)),
                y=alt.Y("Share of orders:Q", title="Share of orders",
                        axis=alt.Axis(format="%", labelFontSize=11)),
                tooltip=[
                    alt.Tooltip("Share of sellers (largest first):Q", title="Seller share", format=".1%"),
                    alt.Tooltip("Share of orders:Q", title="Order share", format=".1%"),
                ],
            )
            diag_line = alt.Chart(diagonal).mark_line(color="#94a3b8", strokeDash=[4, 3], strokeWidth=1.2).encode(
                x="Share of sellers (largest first):Q",
                y="Share of orders:Q",
            )
            show((curve_line + diag_line).properties(
                height=360,
                title=alt.TitleParams(
                    "Marketplace is very concentrated",
                    subtitle=f"Top 5% of sellers handle {top5_order_share:.0%} of all orders",
                    fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                ),
            ))

    section_card(
        "EDA · Category rates & seller size distribution",
        None,
        eda34_body,
        source="processed_data/master_orders.csv",
        analyst="Kannan S", report_key="Seller performance", key_suffix="seller-eda34",
    )

    # ── Q1 — Concentration curve ─────────────────────────────────────────────
    def _curve(col):
        v = st_df.sort_values(col, ascending=False)[col].clip(lower=0)
        xs = np.arange(1, len(v) + 1) / len(v)
        ys = v.cumsum().values / (v.sum() + 1e-9)
        return xs, ys

    x_bad, y_bad = _curve("n_bad")
    x_ord, y_ord = _curve("n_orders")
    x_exc, y_exc = _curve("excess_bad")

    def _at(f, xs, ys):
        return float(np.interp(f, xs, ys))

    conc_df = pd.concat([
        pd.DataFrame({"Share of sellers": x_ord, "Cumulative share": y_ord, "Metric": "Orders (fair benchmark)"}),
        pd.DataFrame({"Share of sellers": x_bad, "Cumulative share": y_bad, "Metric": "Bad reviews"}),
        pd.DataFrame({"Share of sellers": x_exc, "Cumulative share": y_exc, "Metric": "Excess bad reviews (seller's own fault)"}),
    ])

    worst5_bad = _at(0.05, x_bad, y_bad)
    worst5_ord = _at(0.05, x_ord, y_ord)
    worst5_exc = _at(0.05, x_exc, y_exc)

    # ── Q1 — Three definitions of "worst 5%" ─────────────────────────────────
    n5q = max(1, int(0.05 * len(qual)))
    n5a = max(1, int(0.05 * len(st_df)))
    TO = st_df["n_orders"].sum()
    TB = st_df["n_bad"].sum()
    TG = st_df["gmv"].sum()
    TE = st_df["excess_bad"].clip(lower=0).sum() + 1e-9

    groups_def = {
        "By bad-review count": st_df.nlargest(n5a, "n_bad"),
        "By excess bad reviews": qual.nlargest(n5q, "excess_bad"),
        "By bad-review rate": qual.nlargest(n5q, "bad_rate"),
    }
    def_rows = []
    for label, v in groups_def.items():
        their_rate = v["n_bad"].sum() / (v["n_orders"].sum() + 1e-9)
        for metric, val in [
            ("Orders", v["n_orders"].sum() / TO),
            ("GMV", v["gmv"].sum() / TG),
            ("Bad reviews", v["n_bad"].sum() / TB),
            ("Excess damage", v["excess_bad"].clip(lower=0).sum() / TE),
        ]:
            def_rows.append({"Ranked by": label, "Metric": metric, "Share": val * 100,
                              "bad_rate": their_rate})
    def_df = pd.DataFrame(def_rows)

    def q1_row_body():
        c1, c2 = st.columns(2)
        with c1:
            line = alt.Chart(conc_df).mark_line(strokeWidth=2).encode(
                x=alt.X("Share of sellers:Q", title="Share of sellers (worst first)",
                        axis=alt.Axis(format="%", labelFontSize=12)),
                y=alt.Y("Cumulative share:Q", title="Cumulative share",
                        axis=alt.Axis(format="%", labelFontSize=12)),
                color=alt.Color("Metric:N", scale=alt.Scale(
                    domain=["Orders (fair benchmark)", "Bad reviews", "Excess bad reviews (seller's own fault)"],
                    range=["#94a3b8", "#2563eb", "#e11d48"],
                ), legend=alt.Legend(title=None, orient="bottom", direction="vertical", labelFontSize=11)),
                tooltip=[
                    alt.Tooltip("Share of sellers:Q", title="Seller share", format=".1%"),
                    alt.Tooltip("Cumulative share:Q", title="Cumulative share", format=".1%"),
                    alt.Tooltip("Metric:N", title="Metric"),
                ],
            ).properties(
                height=360,
                title=alt.TitleParams(
                    "Damage concentration vs volume",
                    subtitle=f"Worst 5% = {worst5_bad:.0%} of bad reviews, {worst5_ord:.0%} of orders",
                    fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                ),
            )
            show(line)
        with c2:
            chart = alt.Chart(def_df).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
                y=alt.Y("Metric:N", sort=["Orders", "GMV", "Bad reviews", "Excess damage"],
                        title=None, axis=alt.Axis(labelFontSize=11)),
                x=alt.X("Share:Q", title="Share of platform (%)", axis=alt.Axis(labelFontSize=11)),
                color=alt.Color("Metric:N", scale=alt.Scale(
                    domain=["Orders", "GMV", "Bad reviews", "Excess damage"],
                    range=["#2563eb", "#0891b2", "#e11d48", "#dc2626"],
                ), legend=alt.Legend(title=None, orient="bottom", direction="horizontal", labelFontSize=11)),
                row=alt.Row("Ranked by:N", title=None,
                            header=alt.Header(labelFontSize=11, labelAlign="left")),
                tooltip=[
                    alt.Tooltip("Ranked by:N", title="Method"),
                    alt.Tooltip("Metric:N", title="Metric"),
                    alt.Tooltip("Share:Q", title="Share (%)", format=".1f"),
                ],
            ).properties(height=110)
            show(chart)

    section_card(
        "Q1 · Concentration & what 'worst 5%' means",
        "Compare bad-review share against order share — only excess damage is actionable.",
        q1_row_body,
        source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
        analyst="Kannan S", report_key="Seller performance", key_suffix="seller-q1-conc",
    )

    # ── Q2 — Delivery-band test + actual vs expected scatter ─────────────────
    qual_plot = qual.copy()
    qual_plot["Group"] = np.where(qual_plot["offender"], "Offenders", "Other sellers")

    if "band" in single.columns and single["band"].notna().any():
        band_groups = (
            single[single["primary_seller_id"].isin(qual["seller_id"])]
            .groupby(["band", "group"], observed=True)["is_negative"]
            .agg(Orders="size", bad_rate="mean")
            .reset_index()
        )
        band_groups = band_groups[band_groups["Orders"] >= 15].copy()
        band_groups["bad_rate_pct"] = band_groups["bad_rate"] * 100

        def q2_delivery_scatter_body():
            c1, c2 = st.columns(2)
            with c1:
                chart_del = alt.Chart(band_groups).mark_bar().encode(
                    x=alt.X("band:N", sort=None, title="Delivery band",
                            axis=alt.Axis(labelFontSize=11, labelAngle=-20)),
                    y=alt.Y("bad_rate_pct:Q", title="Bad-review rate (%)",
                            axis=alt.Axis(labelFontSize=12)),
                    color=alt.Color("group:N", scale=alt.Scale(
                        domain=["Other sellers", "Offenders"], range=["#2563eb", "#e11d48"]
                    ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
                    xOffset="group:N",
                    tooltip=[
                        alt.Tooltip("band:N", title="Band"),
                        alt.Tooltip("group:N", title="Group"),
                        alt.Tooltip("bad_rate_pct:Q", title="Bad-review rate (%)", format=".1f"),
                        alt.Tooltip("Orders:Q", title="Orders", format=","),
                    ],
                ).properties(
                    height=360,
                    title=alt.TitleParams(
                        "Offenders stay worse even on-time",
                        subtitle="Gap is widest for early deliveries",
                        fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                    ),
                )
                show(chart_del)
            with c2:
                chart_sc = alt.Chart(qual_plot).mark_circle(opacity=0.6).encode(
                    x=alt.X("expected_bad_rate:Q", title="Expected bad-review rate",
                            axis=alt.Axis(format="%", labelFontSize=12)),
                    y=alt.Y("bad_rate:Q", title="Actual bad-review rate",
                            axis=alt.Axis(format="%", labelFontSize=12)),
                    color=alt.Color("Group:N", scale=alt.Scale(
                        domain=["Other sellers", "Offenders"], range=["#2563ebb0", "#e11d48"]
                    ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
                    size=alt.Size("n_orders:Q", title="Orders", scale=alt.Scale(range=[20, 300])),
                    tooltip=[
                        alt.Tooltip("seller_id:N", title="Seller ID"),
                        alt.Tooltip("n_orders:Q", title="Orders", format=","),
                        alt.Tooltip("bad_rate:Q", title="Actual bad-review rate", format=".1%"),
                        alt.Tooltip("expected_bad_rate:Q", title="Expected bad-review rate", format=".1%"),
                        alt.Tooltip("Group:N", title="Group"),
                    ],
                ).properties(
                    height=360,
                    title=alt.TitleParams(
                        "Actual vs expected bad-review rate",
                        subtitle="Above the diagonal = seller's own contribution",
                        fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                    ),
                )
                diag_max = max(qual_plot["expected_bad_rate"].max(), qual_plot["bad_rate"].max()) * 1.05
                diag = pd.DataFrame({"x": [0, diag_max], "y": [0, diag_max]})
                diag_line = alt.Chart(diag).mark_line(color="#0f172a", strokeWidth=1).encode(
                    x=alt.X("x:Q"), y=alt.Y("y:Q"),
                )
                show(chart_sc + diag_line)

        section_card(
            "Q2 · Is it the delivery — or the seller?",
            "Offenders are worse in every delivery band, and above the diagonal even when couriers are on time.",
            q2_delivery_scatter_body,
            source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
            analyst="Kannan S", report_key="Seller performance", key_suffix="seller-q2-delivery",
        )
    else:
        qual_plot = qual.copy()
        qual_plot["Group"] = np.where(qual_plot["offender"], "Offenders", "Other sellers")

        def q2_scatter_only_body():
            chart_sc = alt.Chart(qual_plot).mark_circle(opacity=0.6).encode(
                x=alt.X("expected_bad_rate:Q", title="Expected bad-review rate",
                        axis=alt.Axis(format="%", labelFontSize=12)),
                y=alt.Y("bad_rate:Q", title="Actual bad-review rate",
                        axis=alt.Axis(format="%", labelFontSize=12)),
                color=alt.Color("Group:N", scale=alt.Scale(
                    domain=["Other sellers", "Offenders"], range=["#2563ebb0", "#e11d48"]
                ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
                size=alt.Size("n_orders:Q", title="Orders", scale=alt.Scale(range=[20, 300])),
                tooltip=[
                    alt.Tooltip("seller_id:N", title="Seller ID"),
                    alt.Tooltip("n_orders:Q", title="Orders", format=","),
                    alt.Tooltip("bad_rate:Q", title="Actual bad-review rate", format=".1%"),
                    alt.Tooltip("expected_bad_rate:Q", title="Expected bad-review rate", format=".1%"),
                    alt.Tooltip("Group:N", title="Group"),
                ],
            ).properties(height=420)
            diag_max = max(qual_plot["expected_bad_rate"].max(), qual_plot["bad_rate"].max()) * 1.05
            diag = pd.DataFrame({"x": [0, diag_max], "y": [0, diag_max]})
            diag_line = alt.Chart(diag).mark_line(color="#0f172a", strokeWidth=1).encode(
                x=alt.X("x:Q"), y=alt.Y("y:Q"),
            )
            show(chart_sc + diag_line)

        section_card(
            "Q2 · Actual vs expected bad-review rate",
            "Each dot is one seller (10+ orders). The diagonal = exactly as expected.",
            q2_scatter_only_body,
            source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
            analyst="Kannan S", report_key="Seller performance", key_suffix="seller-q2-scatter",
        )

    # ── Q2 — Persistence heatmap ─────────────────────────────────────────────
    if "order_purchase_timestamp" in single.columns and single["order_purchase_timestamp"].notna().any():
        b = single.sort_values("order_purchase_timestamp").copy()
        b["i"] = b.groupby("primary_seller_id").cumcount()
        b["n"] = b["primary_seller_id"].map(b.groupby("primary_seller_id").size())
        b["half"] = np.where(b["i"] < b["n"] / 2, "H1", "H2")

        sp = (b[b["n"] >= 20]
              .pivot_table(index="primary_seller_id", columns="half", values="is_negative", aggfunc="mean")
              .dropna())
        if len(sp) >= 20:
            QL = ["Q1 best", "Q2", "Q3", "Q4 worst"]
            sp["q1"] = pd.qcut(sp["H1"].rank(method="first"), 4, labels=QL)
            sp["q2"] = pd.qcut(sp["H2"].rank(method="first"), 4, labels=QL)
            trans = pd.crosstab(sp["q1"], sp["q2"], normalize="index")
            persist_worst = trans.loc["Q4 worst", "Q4 worst"] if "Q4 worst" in trans.index else 0.25

            heat_rows = []
            for r in trans.index:
                for c in trans.columns:
                    heat_rows.append({"First half": r, "Second half": c, "Share": trans.loc[r, c]})
            heat_df = pd.DataFrame(heat_rows)
            heat_df["Label"] = (heat_df["Share"] * 100).round(0).astype(int).astype(str) + "%"

            median_rate = qual["bad_rate"].median() if not off.empty else None
            if not off.empty:
                coach_avoided = off["n_bad"].sum() - off["n_orders"].sum() * median_rate
                coach_rate = (TB - coach_avoided) / (TO + 1e-9)
                delist_rate = (TB - off["n_bad"].sum()) / (TO - off["n_orders"].sum() + 1e-9)
                coach_improvement = (BAD_RATE - coach_rate) * 100
                delist_improvement = (BAD_RATE - delist_rate) * 100
                gmv_lost = off["gmv"].sum() / TG * 100
                action_df = pd.DataFrame([
                    {"Option": "Today", "GMV given up (%)": 0.0, "Bad-rate improvement (pp)": 0.0},
                    {"Option": "Coach offenders", "GMV given up (%)": 0.0, "Bad-rate improvement (pp)": coach_improvement},
                    {"Option": "Delist offenders", "GMV given up (%)": gmv_lost, "Bad-rate improvement (pp)": delist_improvement},
                ])

            def q2_persist_action_body():
                c1, c2 = st.columns(2)
                with c1:
                    rect = alt.Chart(heat_df).mark_rect().encode(
                        x=alt.X("Second half:N", sort=QL, title="Quartile in second half",
                                axis=alt.Axis(labelFontSize=12)),
                        y=alt.Y("First half:N", sort=QL, title="Quartile in first half",
                                axis=alt.Axis(labelFontSize=12)),
                        color=alt.Color("Share:Q", scale=alt.Scale(scheme="blues"),
                                        legend=alt.Legend(title="Share", format=".0%")),
                        tooltip=[
                            alt.Tooltip("First half:N", title="First half"),
                            alt.Tooltip("Second half:N", title="Second half"),
                            alt.Tooltip("Share:Q", title="Share", format=".0%"),
                        ],
                    )
                    text = alt.Chart(heat_df).mark_text(fontSize=12).encode(
                        x=alt.X("Second half:N", sort=QL),
                        y=alt.Y("First half:N", sort=QL),
                        text="Label:N",
                        color=alt.condition(alt.datum.Share > 0.28, alt.value("white"), alt.value("black")),
                    )
                    show((rect + text).properties(
                        height=320,
                        title=alt.TitleParams(
                            "Bad sellers mostly stay bad",
                            subtitle=f"Worst-quartile stays worst {persist_worst:.0%} of the time vs 25% by chance",
                            fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                        ),
                    ))
                with c2:
                    if not off.empty:
                        chart_act = alt.Chart(action_df).mark_circle(size=200).encode(
                            x=alt.X("GMV given up (%):Q", title="GMV given up (%)",
                                    scale=alt.Scale(domain=[-1, max(gmv_lost * 1.3, 5)]),
                                    axis=alt.Axis(labelFontSize=12)),
                            y=alt.Y("Bad-rate improvement (pp):Q", title="Bad-review rate improvement (pp)",
                                    scale=alt.Scale(domain=[-0.2, max(coach_improvement, delist_improvement) * 1.3]),
                                    axis=alt.Axis(labelFontSize=12)),
                            color=alt.Color("Option:N", scale=alt.Scale(
                                domain=["Today", "Coach offenders", "Delist offenders"],
                                range=["#94a3b8", "#2563eb", "#e11d48"],
                            ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
                            tooltip=[
                                alt.Tooltip("Option:N", title="Option"),
                                alt.Tooltip("GMV given up (%):Q", title="GMV given up (%)", format=".1f"),
                                alt.Tooltip("Bad-rate improvement (pp):Q", title="Improvement (pp)", format=".2f"),
                            ],
                        ).properties(
                            height=320,
                            title=alt.TitleParams(
                                "Coaching beats delisting on both axes",
                                subtitle="Better satisfaction gain, no catalogue lost",
                                fontSize=13, subtitleFontSize=11, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
                            ),
                        )
                        show(chart_act)

            section_card(
                "Q2 · Persistence & intervention",
                "Bad performance persists — and coaching beats delisting.",
                q2_persist_action_body,
                source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
                analyst="Kannan S", report_key="Seller performance", key_suffix="seller-q2-persist",
            )

# --------------------------------------------------------------------------
# Tab 5 — Route Risk
# --------------------------------------------------------------------------

def render_regions(df):
    page_header(
        "Regional logistics", "Do Certain Regions Experience Systematically Worse Delivery and Satisfaction?",
        "96,476 unique delivered orders · states with ≥ 100 orders · routes with ≥ 30 orders · two questions: state-level patterns and seller → customer route hotspots.",
        "Anushka",
    )
    d = reviewed_delivered(df)

    # ── Q1 data: state-level aggregation matching Anushka's notebook ─────────
    state_agg = d.groupby("customer_state").agg(
        Orders=("order_id", "count"),
        Late_rate=("is_late", "mean"),
        Avg_review=("review_score", "mean"),
        Avg_delivery_days=("delivery_days", "mean"),
    ).reset_index()
    state_agg = state_agg[state_agg["Orders"] >= 100].copy()
    state_agg["Late delivery (%)"] = (state_agg["Late_rate"] * 100).round(1)
    state_agg["Avg review score"] = state_agg["Avg_review"].round(2)
    state_agg["Avg delivery days"] = state_agg["Avg_delivery_days"].round(1)

    top10_late = state_agg.sort_values("Late delivery (%)", ascending=False).head(10)
    bottom10_review = state_agg.sort_values("Avg review score", ascending=True).head(10)

    # Chart A — top 10 states by late delivery rate
    chart_late_states = alt.Chart(top10_late).mark_bar(
        cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#e11d48"
    ).encode(
        x=alt.X("customer_state:N", sort=alt.EncodingSortField("Late delivery (%)", order="descending"),
                title="Customer State", axis=alt.Axis(labelFontSize=13, titleFontSize=13, labelPadding=6)),
        y=alt.Y("Late delivery (%):Q", title="Late Delivery (%)", scale=alt.Scale(domain=[0, 25]),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        tooltip=[
            alt.Tooltip("customer_state:N", title="State"),
            alt.Tooltip("Late delivery (%):Q", title="Late delivery (%)", format=".1f"),
            alt.Tooltip("Orders:Q", title="Orders", format=","),
            alt.Tooltip("Avg review score:Q", title="Avg review score", format=".2f"),
        ],
    ).properties(
        height=420,
        title=alt.TitleParams(
            "Top 10 States by Late Delivery Rate",
            subtitle="States with ≥ 100 orders · sorted by late-delivery % descending",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
        ),
    )

    # Chart B — bottom 10 states by average review score
    chart_review_states = alt.Chart(bottom10_review).mark_bar(
        cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#2563eb"
    ).encode(
        x=alt.X("customer_state:N", sort=alt.EncodingSortField("Avg review score", order="ascending"),
                title="Customer State", axis=alt.Axis(labelFontSize=13, titleFontSize=13, labelPadding=6)),
        y=alt.Y("Avg review score:Q", title="Average Review Score", scale=alt.Scale(domain=[3.7, 4.3], zero=False),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        tooltip=[
            alt.Tooltip("customer_state:N", title="State"),
            alt.Tooltip("Avg review score:Q", title="Avg review score", format=".2f"),
            alt.Tooltip("Orders:Q", title="Orders", format=","),
            alt.Tooltip("Late delivery (%):Q", title="Late delivery (%)", format=".1f"),
        ],
    ).properties(
        height=420,
        title=alt.TitleParams(
            "Bottom 10 States by Average Review Score",
            subtitle="States with ≥ 100 orders · sorted by avg review score ascending",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
        ),
    )

    def q1_body():
        show(chart_late_states)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            'States with fewer than 100 orders excluded (RR, AC, AP dropped). '
            'Average delay_days is negative across all states because early deliveries offset late ones in the average — '
            'late delivery % is the more direct indicator.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q1 · Do certain regions experience systematically worse delivery and satisfaction?",
        None,
        q1_body,
        takeaway="AL has the highest late-delivery rate at 21.4% with a 3.86 review score. MA has the lowest review score at 3.83 with 17.4% late. The same states cluster at the top of both rankings.",
        source="analysis/Anushka/Regional_Logistics_Analysis.ipynb · analysis/Anushka/Regional_Logistics_Report.pdf",
        analyst="Anushka", report_key="Regional logistics", key_suffix="region-q1",
    )

    # ── Q2 data: route-level aggregation matching Anushka's notebook ─────────
    routes_agg = d.groupby(["seller_state", "customer_state"]).agg(
        Orders=("order_id", "nunique"),
        Late_rate=("is_late", "mean"),
        Avg_review=("review_score", "mean"),
        Avg_delivery_days=("delivery_days", "mean"),
    ).reset_index()
    routes_agg = routes_agg[routes_agg["Orders"] >= 30].copy()
    routes_agg["Late delivery (%)"] = (routes_agg["Late_rate"] * 100).round(1)
    routes_agg["Avg review score"] = routes_agg["Avg_review"].round(2)
    routes_agg["Avg delivery days"] = routes_agg["Avg_delivery_days"].round(1)
    routes_agg["Route"] = routes_agg["seller_state"] + " → " + routes_agg["customer_state"]

    top15_late_routes = routes_agg.sort_values("Late delivery (%)", ascending=False).head(15)
    bottom15_review_routes = routes_agg.sort_values("Avg review score", ascending=True).head(15)

    # Chart C — top 15 routes by late delivery rate
    chart_late_routes = alt.Chart(top15_late_routes).mark_bar(
        cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#e11d48"
    ).encode(
        x=alt.X("Route:N", sort=alt.EncodingSortField("Late delivery (%)", order="descending"),
                title="Seller State → Customer State",
                axis=alt.Axis(labelFontSize=11, titleFontSize=12, labelAngle=-45, labelPadding=6)),
        y=alt.Y("Late delivery (%):Q", title="Late Delivery (%)",
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        tooltip=[
            alt.Tooltip("Route:N", title="Route"),
            alt.Tooltip("Late delivery (%):Q", title="Late delivery (%)", format=".1f"),
            alt.Tooltip("Orders:Q", title="Orders", format=","),
            alt.Tooltip("Avg review score:Q", title="Avg review score", format=".2f"),
            alt.Tooltip("Avg delivery days:Q", title="Avg delivery days", format=".1f"),
        ],
    ).properties(
        height=430,
        title=alt.TitleParams(
            "Top 15 Routes by Late Delivery Rate",
            subtitle="Routes with ≥ 30 orders · seller state → customer state",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
        ),
    )

    # Chart D — bottom 15 routes by review score
    chart_review_routes = alt.Chart(bottom15_review_routes).mark_bar(
        cornerRadiusTopLeft=3, cornerRadiusTopRight=3, color="#2563eb"
    ).encode(
        x=alt.X("Route:N", sort=alt.EncodingSortField("Avg review score", order="ascending"),
                title="Seller State → Customer State",
                axis=alt.Axis(labelFontSize=11, titleFontSize=12, labelAngle=-45, labelPadding=6)),
        y=alt.Y("Avg review score:Q", title="Average Review Score", scale=alt.Scale(domain=[3.3, 4.3], zero=False),
                axis=alt.Axis(labelFontSize=12, titleFontSize=13)),
        tooltip=[
            alt.Tooltip("Route:N", title="Route"),
            alt.Tooltip("Avg review score:Q", title="Avg review score", format=".2f"),
            alt.Tooltip("Orders:Q", title="Orders", format=","),
            alt.Tooltip("Late delivery (%):Q", title="Late delivery (%)", format=".1f"),
        ],
    ).properties(
        height=430,
        title=alt.TitleParams(
            "Bottom 15 Routes by Average Review Score",
            subtitle="Routes with ≥ 30 orders · seller state → customer state",
            fontSize=14, subtitleFontSize=12, color="#0f172a", subtitleColor="#64748b", anchor="start", dy=-4,
        ),
    )

    def q2_body():
        show(chart_late_routes)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            'PR → AL: 32.6% late, 3.44 avg review — highest late rate and lowest review score. '
            'RJ → CE: 23.2% late, 3.55 review. '
            'SP → AL (256 orders) and SP → MA (493 orders) are operationally critical — high late rates with larger volumes.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Q2 · Which seller → customer routes perform worst?",
        None,
        q2_body,
        takeaway="PR → AL is the strongest hotspot: 32.6% late and a 3.44 review score. SP → AL and SP → MA matter most operationally — high risk combined with high order volumes.",
        source="analysis/Anushka/Regional_Logistics_Analysis.ipynb · analysis/Anushka/Regional_Logistics_Report.pdf",
        analyst="Anushka", report_key="Regional logistics", key_suffix="region-q2",
    )

    # ── Geographic maps (pydeck choropleth) ─────────────────────────────────
    @st.cache_data(show_spinner=False)
    def load_brazil_geojson():
        path = os.path.join(os.path.dirname(__file__), "brazil_states.geojson")
        with open(path) as f:
            return json.load(f)

    def _interp_red(norm):
        # 0→light pink, 1→dark red
        r = int(255)
        g = int(220 - norm * 200)
        b = int(220 - norm * 200)
        return [max(0, r), max(0, g), max(0, b), 220]

    def _interp_blue_red(norm):
        # 0→dark red (low score), 1→dark blue (high score)
        if norm < 0.5:
            t = norm * 2
            return [int(200 - t * 50), int(t * 50), int(t * 80), 220]
        else:
            t = (norm - 0.5) * 2
            return [int(150 - t * 150), int(50 + t * 100), int(80 + t * 175), 220]

    def render_geo_maps():
        geojson = load_brazil_geojson()

        late_lookup = state_agg.set_index("customer_state")["Late delivery (%)"].to_dict()
        review_lookup = state_agg.set_index("customer_state")["Avg review score"].to_dict()
        orders_lookup = state_agg.set_index("customer_state")["Orders"].to_dict()

        late_vals = [v for v in late_lookup.values()]
        late_min, late_max = min(late_vals), max(late_vals)
        rev_vals = [v for v in review_lookup.values()]
        rev_min, rev_max = min(rev_vals), max(rev_vals)

        late_features, review_features = [], []
        for feat in geojson["features"]:
            abbr = feat["properties"].get("sigla", "")
            base = {**feat, "properties": {**feat["properties"], "state": abbr}}

            if abbr in late_lookup:
                norm = (late_lookup[abbr] - late_min) / (late_max - late_min + 1e-9)
                late_features.append({**base, "properties": {
                    **base["properties"],
                    "late_pct": late_lookup[abbr],
                    "avg_review": review_lookup.get(abbr, "n/a"),
                    "orders": orders_lookup.get(abbr, "n/a"),
                    "fill_color": _interp_red(norm),
                }})

            if abbr in review_lookup:
                norm = (review_lookup[abbr] - rev_min) / (rev_max - rev_min + 1e-9)
                review_features.append({**base, "properties": {
                    **base["properties"],
                    "avg_review": review_lookup[abbr],
                    "late_pct": late_lookup.get(abbr, "n/a"),
                    "orders": orders_lookup.get(abbr, "n/a"),
                    "fill_color": _interp_blue_red(norm),
                }})

        view = pdk.ViewState(latitude=-14.2, longitude=-51.9, zoom=3.2, pitch=0)

        late_layer = pdk.Layer(
            "GeoJsonLayer",
            data={"type": "FeatureCollection", "features": late_features},
            stroked=True, filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[255, 255, 255, 220],
            line_width_min_pixels=1,
            pickable=True, auto_highlight=True,
        )
        review_layer = pdk.Layer(
            "GeoJsonLayer",
            data={"type": "FeatureCollection", "features": review_features},
            stroked=True, filled=True,
            get_fill_color="properties.fill_color",
            get_line_color=[255, 255, 255, 220],
            line_width_min_pixels=1,
            pickable=True, auto_highlight=True,
        )

        tooltip_late = {
            "html": "<b>{state}</b><br/>Late delivery: <b>{late_pct}%</b><br/>Avg review: {avg_review}<br/>Orders: {orders}",
            "style": {"background": "#0f172a", "color": "white", "fontSize": "13px", "padding": "8px 12px", "borderRadius": "6px"},
        }
        tooltip_review = {
            "html": "<b>{state}</b><br/>Avg review score: <b>{avg_review}</b><br/>Late delivery: {late_pct}%<br/>Orders: {orders}",
            "style": {"background": "#0f172a", "color": "white", "fontSize": "13px", "padding": "8px 12px", "borderRadius": "6px"},
        }

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:6px;">Late Delivery Rate by State · darker red = higher late rate</div>', unsafe_allow_html=True)
            st.pydeck_chart(pdk.Deck(
                layers=[late_layer], initial_view_state=view,
                tooltip=tooltip_late, map_style="light",
            ), height=460)
        with c2:
            st.markdown('<div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:6px;">Avg Review Score by State · red = low · blue = high</div>', unsafe_allow_html=True)
            st.pydeck_chart(pdk.Deck(
                layers=[review_layer], initial_view_state=view,
                tooltip=tooltip_review, map_style="light",
            ), height=460)
        st.markdown(
            '<div class="sec-caption" style="margin-top:6px;">'
            'States with fewer than 100 orders excluded (RR, AC, AP shown but no data). '
            'Hover any state for exact values.'
            '</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "Geographic view — delivery and satisfaction by state",
        None,
        render_geo_maps,
        source="analysis/Anushka/Regional_Logistics_Report.pdf",
        analyst="Anushka", report_key="Regional logistics", key_suffix="region-geomap",
    )


# --------------------------------------------------------------------------
# Tab 6 — Product Risk  (Ashwanth V)
# --------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_product_base():
    """Build Ashwanth's analytical base: delivered+reviewed orders joined to product features."""
    master = load_master()
    base = master[(master["order_status"] == "delivered") & master["review_score"].notna()].copy()
    base["is_bad"] = base["is_negative"].map({True: 1, False: 0})
    base["is_ontime"] = base["is_late"].map({True: False, False: True})

    prod_path = os.path.join(DATA_DIR, "products.csv")
    items_path = os.path.join(DATA_DIR, "order_items.csv")
    if not os.path.exists(prod_path) or not os.path.exists(items_path):
        return base, pd.DataFrame()

    products = pd.read_csv(prod_path, low_memory=False)
    items = pd.read_csv(items_path, low_memory=False)

    top_item = (
        items.sort_values("price", ascending=False)
        .drop_duplicates("order_id")[["order_id", "product_id"]]
    )
    prod_cols = ["product_id", "product_description_length", "product_photos_qty",
                 "product_weight_g", "product_volume_cm3", "product_category_name_english"]
    prod_cols = [c for c in prod_cols if c in products.columns]
    base = (
        base.merge(top_item, on="order_id", how="left")
            .merge(products[prod_cols], on="product_id", how="left")
    )
    if "product_category_name_english" in base.columns:
        base["category"] = base["product_category_name_english"].fillna(
            base.get("primary_category", "unknown")
        )
    else:
        base["category"] = base.get("primary_category", "unknown")

    # revenue column (total_price already in master)
    base["revenue"] = pd.to_numeric(base["total_price"], errors="coerce")
    return base, products


def _bad_by_bins(df, col, n_bins=7, min_n=100, log_scale=False):
    """Replicate Ashwanth's bad_by_bins helper — returns a tidy DataFrame."""
    sub = df[[col, "is_bad"]].dropna()
    if log_scale:
        sub = sub[sub[col] > 0].copy()
        sub[col] = np.log1p(sub[col])
    try:
        sub["bin"] = pd.qcut(sub[col], n_bins, duplicates="drop")
    except Exception:
        sub["bin"] = pd.cut(sub[col], n_bins)
    tbl = (
        sub.groupby("bin", observed=True)
        .agg(n=("is_bad", "size"), bad_rate=("is_bad", "mean"))
        .reset_index()
    )
    tbl = tbl[tbl["n"] >= min_n].copy()
    tbl["mid"] = tbl["bin"].apply(lambda b: (b.left + b.right) / 2 if log_scale else (b.left + b.right) / 2)
    tbl["label"] = tbl["bin"].astype(str)
    tbl["bad_pct"] = tbl["bad_rate"] * 100
    return tbl


def _bin_bar(tbl, baseline, x_title, color="#2563eb", height=260):
    """Horizontal bar chart for a binned bad-rate breakdown."""
    y_min = max(0, min(tbl["bad_pct"].min() * 0.85, baseline * 0.85))
    y_max = max(tbl["bad_pct"].max(), baseline) * 1.15
    y_scale = alt.Scale(domain=[y_min, y_max])
    baseline_rule = alt.Chart(pd.DataFrame({"y": [baseline]})).mark_rule(
        color="#64748b", strokeDash=[4, 3], strokeWidth=1.5
    ).encode(y=alt.Y("y:Q", scale=y_scale))
    bars = alt.Chart(tbl).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("label:N", sort=tbl["label"].tolist(), title=x_title,
                axis=alt.Axis(labelAngle=-30, labelFontSize=11)),
        y=alt.Y("bad_pct:Q", title="Bad-review rate (%)", scale=y_scale),
        color=alt.value(color),
        tooltip=[
            alt.Tooltip("label:N", title=x_title),
            alt.Tooltip("bad_pct:Q", title="Bad-review rate (%)", format=".1f"),
            alt.Tooltip("n:Q", title="Orders", format=","),
        ],
    ).properties(height=height)
    return bars + baseline_rule


def render_products(df):
    page_header(
        "Product portfolio", "Which Products Generate Revenue but Disappoint Customers?",
        "Beyond delivery, what else moves the score — and which categories carry high revenue with poor satisfaction?",
        "Ashwanth V",
    )

    base, _ = _load_product_base()
    if base.empty:
        st.warning("Product data not available.")
        return

    BAD_RATE = base["is_bad"].mean()
    ontime = base[base["is_ontime"] == True].copy()

    # ── Q1 — Feature ranking ─────────────────────────────────────────────────
    feature_defs = [
        ("freight_ratio",               "Freight ratio",          True,  False),
        ("total_price",                  "Order price",            True,  True),
        ("n_items",                      "No. of items",           False, False),
        ("product_weight_g",             "Product weight",         True,  True),
        ("product_volume_cm3",           "Product volume",         True,  True),
        ("product_description_length",   "Description length",     True,  True),
        ("product_photos_qty",           "Photo count",            False, True),
    ]

    ranking_rows = []
    for col, label, _, __ in feature_defs:
        if col not in ontime.columns:
            continue
        sub = ontime[[col, "is_bad"]].dropna()
        sub = sub[pd.to_numeric(sub[col], errors="coerce").notna()]
        sub[col] = pd.to_numeric(sub[col], errors="coerce")
        sub = sub.dropna()
        if len(sub) < 100:
            continue
        r, p = pointbiserialr(sub["is_bad"], sub[col])
        ranking_rows.append({"Feature": label, "r": r, "abs_r": abs(r), "p": p,
                              "Direction": "→ worse" if r > 0 else "→ better"})

    def q1_ranking_body():
        if not ranking_rows:
            st.caption("Insufficient data to rank features.")
            return
        fdf = pd.DataFrame(ranking_rows).sort_values("abs_r", ascending=False)
        fdf["r_pct"] = fdf["r"] * 100
        chart = alt.Chart(fdf).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("Feature:N", sort=fdf["Feature"].tolist(), title=None,
                    axis=alt.Axis(labelFontSize=12)),
            y=alt.Y("r_pct:Q", title="Point-biserial r × 100",
                    scale=alt.Scale(domain=[fdf["r_pct"].min() * 1.2, fdf["r_pct"].max() * 1.2])),
            color=alt.condition(
                alt.datum.r_pct > 0,
                alt.value("#e11d48"),
                alt.value("#059669"),
            ),
            tooltip=[
                alt.Tooltip("Feature:N"),
                alt.Tooltip("r_pct:Q", title="r × 100", format=".2f"),
                alt.Tooltip("Direction:N"),
            ],
        ).properties(height=300)
        show(chart)

    section_card(
        "Q1 · Feature ranking — what moves the score on on-time orders?",
        "Point-biserial correlation between each product/pricing feature and bad reviews, restricted to on-time orders to remove the delivery signal. Red = higher value → more bad reviews; green = higher value → fewer.",
        q1_ranking_body,
        takeaway="Freight ratio is the strongest non-delivery driver: orders where shipping cost is a large fraction of item value get nearly 2× the bad-review rate.",
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q1-ranking",
    )

    # ── Q1 — per-feature bin breakdowns ──────────────────────────────────────
    ontime_baseline = ontime["is_bad"].mean() * 100

    # Pre-compute tables for the three Q1 bin sections (same logic as notebook)
    _tbl_price = _bad_by_bins(ontime, "total_price", n_bins=8, log_scale=True)
    _tbl_fr    = _bad_by_bins(ontime, "freight_ratio", n_bins=8, log_scale=False)

    _sub_wt   = ontime.dropna(subset=["product_weight_g"])
    _tbl_wt   = _bad_by_bins(_sub_wt, "product_weight_g", n_bins=7, log_scale=True)
    _sub_vol  = ontime[ontime["product_volume_cm3"] > 0].dropna(subset=["product_volume_cm3"])
    _tbl_vol  = _bad_by_bins(_sub_vol, "product_volume_cm3", n_bins=7, log_scale=True)
    _sub_desc = ontime.dropna(subset=["product_description_length"])
    _tbl_desc = _bad_by_bins(_sub_desc, "product_description_length", n_bins=7, log_scale=True)

    _sub_ph   = ontime.dropna(subset=["product_photos_qty"]).copy()
    _sub_ph["product_photos_qty"] = pd.to_numeric(_sub_ph["product_photos_qty"], errors="coerce")
    _sub_ph   = _sub_ph.dropna(subset=["product_photos_qty"])
    _ph_tbl   = (
        _sub_ph.assign(photos=_sub_ph["product_photos_qty"].clip(upper=8).astype(int))
        .groupby("photos")["is_bad"]
        .agg(n="size", bad_rate="mean")
        .reset_index()
    )
    _ph_tbl   = _ph_tbl[_ph_tbl["n"] >= 50].copy()
    _ph_tbl["bad_pct"] = _ph_tbl["bad_rate"] * 100
    _ph_baseline = _sub_ph["is_bad"].mean() * 100

    _sub_ni   = ontime.dropna(subset=["n_items"]).copy()
    _sub_ni["n_items"] = pd.to_numeric(_sub_ni["n_items"], errors="coerce")
    _sub_ni   = _sub_ni.dropna(subset=["n_items"])
    _ni_tbl   = (
        _sub_ni.assign(items=_sub_ni["n_items"].clip(upper=5).astype(int))
        .groupby("items")["is_bad"]
        .agg(n="size", bad_rate="mean")
        .reset_index()
    )
    _ni_tbl   = _ni_tbl[_ni_tbl["n"] >= 50].copy()
    _ni_tbl["bad_pct"] = _ni_tbl["bad_rate"] * 100
    _ni_baseline = _sub_ni["is_bad"].mean() * 100

    def _bars(tbl, x_col, x_title, color, height=260):
        return alt.Chart(tbl).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X(f"{x_col}:N", sort=tbl[x_col].tolist(), title=x_title,
                    axis=alt.Axis(labelAngle=-30, labelFontSize=11)),
            y=alt.Y("bad_pct:Q", title="Bad-review rate (%)"),
            color=alt.value(color),
            tooltip=[
                alt.Tooltip(f"{x_col}:N", title=x_title),
                alt.Tooltip("bad_pct:Q", title="Bad-review rate (%)", format=".1f"),
                alt.Tooltip("n:Q", title="Orders", format=","),
            ],
        ).properties(height=height)

    def _legend(*items):
        spans = "".join(
            f'<span><span style="display:inline-block;width:10px;height:10px;background:{c};margin-right:6px;border-radius:2px;"></span>{lbl}</span>'
            for lbl, c in items
        )
        st.markdown(
            f'<div style="display:flex;gap:22px;align-items:center;margin:6px 0 0;color:#475569;font-size:12px;">{spans}</div>',
            unsafe_allow_html=True,
        )

    def q1_bins_body():
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Order price (R$, log bins)")
            if not _tbl_price.empty:
                show(_bars(_tbl_price, "label", "Order price (R$, log bins)", "#2563eb"))
        with c2:
            st.caption("Freight ratio")
            if not _tbl_fr.empty:
                show(_bars(_tbl_fr, "label", "Freight ratio", "#d97706"))
        _legend(("Order price", "#2563eb"), ("Freight ratio", "#d97706"))

    section_card(
        "Q1 · Price and freight ratio",
        "Bad-review rate across bins of order price and freight ratio, on-time orders only.",
        q1_bins_body,
        source="processed_data/master_orders.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q1-price-fr",
    )

    def q1_product_body():
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("Product weight (g, log bins)")
            if not _tbl_wt.empty:
                show(_bars(_tbl_wt, "label", "Product weight (g, log bins)", "#2563eb", height=240))
        with c2:
            st.caption("Product volume (cm³, log bins)")
            if not _tbl_vol.empty:
                show(_bars(_tbl_vol, "label", "Product volume (cm³, log bins)", "#2563eb", height=240))
        with c3:
            st.caption("Description length (chars, log bins)")
            if not _tbl_desc.empty:
                show(_bars(_tbl_desc, "label", "Description length (chars, log bins)", "#059669", height=240))
        _legend(("Weight / Volume", "#2563eb"), ("Description length", "#059669"))

    section_card(
        "Q1 · Product weight, volume, and description length",
        "Heavier and bulkier products score slightly worse; longer descriptions correlate with slightly fewer bad reviews.",
        q1_product_body,
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q1-physical",
    )

    def q1_photos_items_body():
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Photo count (capped at 8)")
            if not _ph_tbl.empty:
                show(alt.Chart(_ph_tbl).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                    x=alt.X("photos:O", title="Photo count (capped at 8)", axis=alt.Axis(labelFontSize=12)),
                    y=alt.Y("bad_pct:Q", title="Bad-review rate (%)"),
                    color=alt.value("#2563eb"),
                    tooltip=[
                        alt.Tooltip("photos:O", title="Photo count"),
                        alt.Tooltip("bad_pct:Q", title="Bad-review rate (%)", format=".1f"),
                        alt.Tooltip("n:Q", title="Orders", format=","),
                    ],
                ).properties(height=260))
        with c2:
            st.caption("Number of items (capped at 5)")
            if not _ni_tbl.empty:
                show(alt.Chart(_ni_tbl).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                    x=alt.X("items:O", title="Number of items (capped at 5)", axis=alt.Axis(labelFontSize=12)),
                    y=alt.Y("bad_pct:Q", title="Bad-review rate (%)"),
                    color=alt.value("#2563eb"),
                    tooltip=[
                        alt.Tooltip("items:O", title="Items"),
                        alt.Tooltip("bad_pct:Q", title="Bad-review rate (%)", format=".1f"),
                        alt.Tooltip("n:Q", title="Orders", format=","),
                    ],
                ).properties(height=260))
        _legend(("Bad-review rate (%)", "#2563eb"))

    section_card(
        "Q1 · Photo count and number of items",
        "More product photos (up to ~4) are associated with fewer bad reviews; multi-item orders have more failure points.",
        q1_photos_items_body,
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q1-photos-items",
    )

    # ── Q2 — category revenue vs satisfaction ───────────────────────────────
    MIN_ORDERS = 200
    cat_tbl = (
        base[base["category"].notna() & (base["category"] != "unknown")]
        .groupby("category")
        .agg(
            n_orders=("order_id", "count"),
            revenue=("revenue", "sum"),
            bad_rate=("is_bad", "mean"),
            avg_score=("review_score", "mean"),
            n_bad=("is_bad", "sum"),
        )
        .query(f"n_orders >= {MIN_ORDERS}")
        .sort_values("revenue", ascending=False)
        .reset_index()
    )
    if cat_tbl.empty:
        st.warning("Insufficient category data.")
        return

    rev_q33 = cat_tbl["revenue"].quantile(0.33)
    rev_q66 = cat_tbl["revenue"].quantile(0.66)
    bad_med = cat_tbl["bad_rate"].median()

    def _segment(row):
        hi = row["revenue"] >= rev_q66
        lo = row["revenue"] < rev_q33
        poor = row["bad_rate"] > bad_med
        if hi and poor:   return "High rev + poor sat"
        if hi:            return "High rev + good sat"
        if lo and poor:   return "Low rev + poor sat"
        return "Low rev + good sat"

    cat_tbl["Segment"] = cat_tbl.apply(_segment, axis=1)
    cat_tbl["Category"] = cat_tbl["category"].str.replace("_", " ")
    cat_tbl["Bad rate (%)"] = (cat_tbl["bad_rate"] * 100).round(1)
    cat_tbl["Revenue (R$M)"] = (cat_tbl["revenue"] / 1e6).round(3)

    SEG_COLORS = {
        "High rev + poor sat": "#d62728",
        "High rev + good sat": "#2a78d6",
        "Low rev + poor sat":  "#eb6834",
        "Low rev + good sat":  "#2ca02c",
    }

    def q2_quadrant_body():
        vline = alt.Chart(pd.DataFrame({"x": [rev_q66 / 1e6]})).mark_rule(
            color="#94a3b8", strokeDash=[4, 3], strokeWidth=1
        ).encode(x=alt.X("x:Q"))
        hline = alt.Chart(pd.DataFrame({"y": [bad_med * 100]})).mark_rule(
            color="#94a3b8", strokeDash=[4, 3], strokeWidth=1
        ).encode(y=alt.Y("y:Q"))
        scatter = alt.Chart(cat_tbl).mark_circle(opacity=0.82).encode(
            x=alt.X("Revenue (R$M):Q", title="Category revenue (R$ millions)"),
            y=alt.Y("Bad rate (%):Q", title="Bad-review rate (%)"),
            size=alt.Size("n_orders:Q", title="Orders", scale=alt.Scale(range=[40, 800])),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEG_COLORS.keys()),
                range=list(SEG_COLORS.values()),
            ), legend=alt.Legend(title=None, orient="bottom", direction="vertical",
                                 labelFontSize=12, padding=8)),
            tooltip=[
                alt.Tooltip("Category:N"),
                alt.Tooltip("n_orders:Q", title="Orders", format=","),
                alt.Tooltip("Revenue (R$M):Q", title="Revenue (R$M)", format=".2f"),
                alt.Tooltip("Bad rate (%):Q", title="Bad-review rate (%)", format=".1f"),
                alt.Tooltip("avg_score:Q", title="Avg review score", format=".2f"),
                alt.Tooltip("Segment:N"),
            ],
        ).properties(height=380)
        show((scatter + vline + hline).resolve_scale(color="shared"))

    section_card(
        "Q2 · Growth versus experience quadrant",
        "Each bubble is a category (min 200 orders). Dashed lines = revenue top-third threshold and median bad-review rate. Upper-right quadrant (red) = high revenue AND poor satisfaction.",
        q2_quadrant_body,
        takeaway="High-revenue + poor-satisfaction categories are the clearest portfolio intervention zone — large commercial exposure with avoidable dissatisfaction.",
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q2-quadrant",
    )

    def q2_revenue_body():
        top25 = cat_tbl.head(25).copy()
        bars = alt.Chart(top25).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
            y=alt.Y("Category:N", sort=alt.EncodingSortField("Revenue (R$M)", order="descending"),
                    title=None, axis=alt.Axis(labelFontSize=11, labelLimit=220)),
            x=alt.X("Revenue (R$M):Q", title="Revenue (R$ millions)"),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEG_COLORS.keys()),
                range=list(SEG_COLORS.values()),
            ), legend=alt.Legend(title=None, orient="bottom", direction="vertical",
                                 labelFontSize=12, padding=8)),
            tooltip=[
                alt.Tooltip("Category:N"),
                alt.Tooltip("Revenue (R$M):Q", title="Revenue (R$M)", format=".2f"),
                alt.Tooltip("Bad rate (%):Q", title="Bad-review rate (%)", format=".1f"),
                alt.Tooltip("n_orders:Q", title="Orders", format=","),
                alt.Tooltip("Segment:N"),
            ],
        ).properties(height=500)
        show(bars)

    section_card(
        "Q2 · Top 25 categories by revenue",
        "Revenue bar chart coloured by quadrant segment. Orange bars = high revenue but poor satisfaction.",
        q2_revenue_body,
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q2-revenue",
    )

    def q2_all_cats_body():
        cat_sorted = cat_tbl.sort_values("Bad rate (%)", ascending=False).copy()
        med_rule = alt.Chart(pd.DataFrame({"x": [bad_med * 100]})).mark_rule(
            color="#64748b", strokeDash=[4, 3], strokeWidth=1.5
        ).encode(x=alt.X("x:Q"))
        bars = alt.Chart(cat_sorted).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
            y=alt.Y("Category:N", sort=alt.EncodingSortField("Bad rate (%)", order="descending"),
                    title=None, axis=alt.Axis(labelFontSize=10, labelLimit=220)),
            x=alt.X("Bad rate (%):Q", title="Bad-review rate (%)", scale=alt.Scale(domain=[0, cat_sorted["Bad rate (%)"].max() * 1.1])),
            color=alt.Color("Segment:N", scale=alt.Scale(
                domain=list(SEG_COLORS.keys()),
                range=list(SEG_COLORS.values()),
            ), legend=alt.Legend(title=None, orient="bottom", direction="vertical",
                                 labelFontSize=12, padding=8)),
            tooltip=[
                alt.Tooltip("Category:N"),
                alt.Tooltip("Bad rate (%):Q", title="Bad-review rate (%)", format=".1f"),
                alt.Tooltip("Revenue (R$M):Q", title="Revenue (R$M)", format=".2f"),
                alt.Tooltip("n_orders:Q", title="Orders", format=","),
                alt.Tooltip("Segment:N"),
            ],
        ).properties(height=max(400, len(cat_sorted) * 16))
        show((bars + med_rule).resolve_scale(color="shared"))

    section_card(
        "Q2 · All categories ranked by bad-review rate",
        "Every category with 200+ orders, sorted by dissatisfaction. Dashed line = median. Colour shows revenue–satisfaction quadrant.",
        q2_all_cats_body,
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V", report_key="Product portfolio", key_suffix="product-q2-all",
    )


# --------------------------------------------------------------------------
# Tab 6 — Seller Behaviour Drivers (Sahib Randhawa)
# --------------------------------------------------------------------------

def render_seller_behaviour(df):
    page_header(
        "Seller behaviour drivers",
        "What Makes a Seller Underperform, and Where to Invest Next",
        "Four seller behaviours tested against bad-review rate, and a ranked investment ladder.",
        "Sahib Randhawa",
    )
    d = reviewed_delivered(df)
    sellers_all = d[d["primary_seller_id"].notna()].copy()
    sellers_all["handling_days"] = pd.to_numeric(sellers_all["handling_days"], errors="coerce")
    sellers_all["freight_ratio"] = pd.to_numeric(sellers_all["freight_ratio"], errors="coerce")
    sellers_all["is_negative_num"] = sellers_all["is_negative"].astype(float)

    # Seller-level aggregation (10+ orders)
    seller_agg = (
        sellers_all.groupby("primary_seller_id")
        .agg(
            n_orders=("order_id", "count"),
            avg_handling=("handling_days", "mean"),
            avg_freight_ratio=("freight_ratio", "mean"),
            n_categories=("n_distinct_categories", "mean"),
            neg_rate=("is_negative_num", "mean"),
        )
        .reset_index()
    )
    seller_agg = seller_agg[seller_agg["n_orders"] >= 10].copy()

    platform_avg = d["is_negative"].mean() * 100

    # --- Section 1: Handling time quartile chart ---
    def handling_quartile_body():
        if seller_agg.empty or seller_agg["avg_handling"].isna().all():
            st.info("Insufficient data to compute handling-time quartiles.")
            return

        valid = seller_agg.dropna(subset=["avg_handling", "neg_rate"])
        labels = ["Q1 fastest\n(avg 1.2d)", "Q2\n(avg 1.8d)", "Q3\n(avg 2.7d)", "Q4 slowest\n(avg 5.6d)"]
        valid = valid.copy()
        valid["quartile"] = pd.qcut(valid["avg_handling"], q=4, labels=labels)
        quartile_rates = (
            valid.groupby("quartile", observed=True)["neg_rate"]
            .mean()
            .reset_index()
            .rename(columns={"quartile": "Handling quartile", "neg_rate": "Bad-review rate %"})
        )
        quartile_rates["Bad-review rate %"] = quartile_rates["Bad-review rate %"] * 100

        base = alt.Chart(quartile_rates).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Handling quartile:N", sort=None, title=None),
            y=alt.Y("Bad-review rate %:Q", title="Bad-review rate (%)"),
            color=alt.condition(
                alt.datum["Handling quartile"] == labels[-1],
                alt.value("#ea580c"),
                alt.value("#2563eb"),
            ),
            tooltip=[
                alt.Tooltip("Handling quartile:N"),
                alt.Tooltip("Bad-review rate %:Q", format=".1f"),
            ],
        ).properties(height=320)

        platform_rule = alt.Chart(pd.DataFrame({"y": [platform_avg]})).mark_rule(
            color="#64748b", strokeDash=[4, 3], strokeWidth=1.5
        ).encode(y="y:Q")

        show(base + platform_rule)
        st.markdown(
            f'<div class="sec-caption">Dashed line = platform average ({platform_avg:.1f}%). '
            f"Sellers in Q4 (slowest handling) run nearly double the bad-review rate of Q1 sellers. "
            f"n = {len(valid):,} sellers with 10+ qualifying orders.</div>",
            unsafe_allow_html=True,
        )

    section_card(
        "1 · Handling time is the strongest seller-side driver of bad reviews",
        "Sellers in the slowest handling-time quartile run nearly double the platform average.",
        handling_quartile_body,
        source="processed_data/master_orders.csv",
        analyst="Sahib Randhawa",
        report_key="Seller behaviour",
        key_suffix="behav-handling",
    )

    # --- Section 2: All four behaviours compared ---
    def four_behaviours_body():
        rows = [
            {"Behaviour": "Handling time", "Pearson r": 0.244, "Spearman ρ": 0.208, "Significant": True},
            {"Behaviour": "Catalogue breadth", "Pearson r": 0.070, "Spearman ρ": 0.092, "Significant": True},
            {"Behaviour": "Freight ratio", "Pearson r": 0.040, "Spearman ρ": 0.066, "Significant": False},
            {"Behaviour": "Volume (log orders)", "Pearson r": 0.018, "Spearman ρ": 0.082, "Significant": False},
        ]
        corr_df = pd.DataFrame(rows)

        chart = alt.Chart(corr_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("Behaviour:N", sort=None, title=None),
            y=alt.Y("Pearson r:Q", title="Pearson r (bivariate correlation with excess bad-review rate)"),
            color=alt.condition(
                alt.datum["Significant"],
                alt.value("#ea580c"),
                alt.value("#94a3b8"),
            ),
            tooltip=[
                alt.Tooltip("Behaviour:N"),
                alt.Tooltip("Pearson r:Q", format=".3f"),
                alt.Tooltip("Spearman ρ:Q", format=".3f"),
            ],
        ).properties(height=300)

        show(chart)

        st.markdown(
            '<div class="sec-caption">'
            "Orange = statistically significant (p &lt; 0.05). "
            "In multiple regression, only handling time (p &lt;0.0001) and catalogue breadth (p=0.035) survive."
            "</div>",
            unsafe_allow_html=True,
        )

    section_card(
        "2 · All four seller behaviours tested together",
        "Handling time dominates; catalogue breadth has a small secondary effect; freight ratio and volume are unreliable.",
        four_behaviours_body,
        source="processed_data/master_orders.csv",
        analyst="Sahib Randhawa",
        report_key="Seller behaviour",
        key_suffix="behav-four",
    )

    # --- Section 3: Handling time within delivery bands ---
    def robustness_body():
        if sellers_all.empty:
            st.info("Insufficient data.")
            return

        valid = sellers_all.dropna(subset=["handling_days", "delay_bucket", "is_negative_num"]).copy()
        if valid.empty:
            st.info("Insufficient data.")
            return

        median_handling = valid["handling_days"].median()
        valid["handling_group"] = valid["handling_days"].apply(
            lambda x: "Fast-handling (below median)" if x < median_handling else "Slow-handling (at/above median)"
        )

        band_order = ["30+ early", "15-30 early", "7-15 early", "3-7 early", "0-3 early", "0-3 late", "3-7 late", "7-15 late", "15-30 late", "30+ late"]
        valid["delay_bucket"] = pd.Categorical(valid["delay_bucket"], categories=band_order, ordered=True)
        grouped = (
            valid.groupby(["delay_bucket", "handling_group"], observed=True)["is_negative_num"]
            .mean()
            .reset_index()
            .rename(columns={"is_negative_num": "Bad-review rate", "delay_bucket": "Delivery band"})
        )
        grouped["Bad-review rate %"] = grouped["Bad-review rate"] * 100

        chart = alt.Chart(grouped).mark_bar().encode(
            x=alt.X("Delivery band:N", sort=band_order, title=None),
            y=alt.Y("Bad-review rate %:Q", title="Bad-review rate (%)"),
            color=alt.Color(
                "handling_group:N",
                scale=alt.Scale(
                    domain=["Fast-handling (below median)", "Slow-handling (at/above median)"],
                    range=["#2563eb", "#ea580c"],
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            xOffset="handling_group:N",
            tooltip=[
                alt.Tooltip("Delivery band:N"),
                alt.Tooltip("handling_group:N", title="Handling group"),
                alt.Tooltip("Bad-review rate %:Q", format=".1f"),
            ],
        ).properties(height=320)

        show(chart)
        st.markdown(
            '<div class="sec-caption">'
            "Gap is largest on early/on-time parcels. Disappears once a parcel is 7+ days late."
            "</div>",
            unsafe_allow_html=True,
        )

    section_card(
        "3 · Slow-handling sellers stay worse even on early and on-time parcels",
        "The handling-time effect survives within every delivery band — it is not just a proxy for slow routes.",
        robustness_body,
        source="processed_data/master_orders.csv",
        analyst="Sahib Randhawa",
        report_key="Seller behaviour",
        key_suffix="behav-robustness",
    )

    # --- Section 4: Investment ladder ---
    def investment_ladder_body():
        ladder = pd.DataFrame([
            {"Lever": "Fix promised delivery date", "Est. pp impact": 3.56, "Status": "Quantified"},
            {"Lever": "Coach 77 flagged sellers (slowest-handling first)", "Est. pp impact": 1.30, "Status": "Quantified"},
            {"Lever": "Category / freight fixes", "Est. pp impact": 0.5, "Status": "TBD — not yet sized"},
            {"Lever": "Regional / worst-route fixes", "Est. pp impact": 0.3, "Status": "Unknown"},
        ])

        chart = alt.Chart(ladder).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
            y=alt.Y("Lever:N", sort=None, title=None,
                    axis=alt.Axis(labelFontSize=12, labelLimit=340)),
            x=alt.X("Est. pp impact:Q", title="Estimated platform bad-review rate improvement (pp)",
                    axis=alt.Axis(labelFontSize=12, titleFontSize=12)),
            color=alt.Color("Status:N", scale=alt.Scale(
                domain=["Quantified", "TBD — not yet sized", "Unknown"],
                range=["#ea580c", "#94a3b8", "#cbd5e1"],
            ), legend=alt.Legend(title=None, orient="bottom", labelFontSize=12)),
            tooltip=[
                alt.Tooltip("Lever:N"),
                alt.Tooltip("Est. pp impact:Q", format=".2f", title="Est. pp impact"),
                alt.Tooltip("Status:N"),
            ],
        ).properties(height=260)

        show(chart)
        st.markdown(
            '<div class="sec-caption">'
            "Orange = directly quantified. Grey = plausible but not yet sized. "
            "Delivery promise fix (~3.56 pp) outweighs seller coaching (1.30 pp) roughly 2.7 to 1."
            "</div>",
            unsafe_allow_html=True,
        )

    section_card(
        "4 · Where to invest — the ranked intervention ladder",
        "Delivery promise fix leads; seller coaching second.",
        investment_ladder_body,
        source="analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf",
        analyst="Sahib Randhawa",
        report_key="Seller behaviour",
        key_suffix="behav-ladder",
    )


# --------------------------------------------------------------------------
# Tab 7 — Recommendations
# --------------------------------------------------------------------------

def render_recommendations(df):
    page_header(
        "The decision", "Recommendations for Growth Without Breaking Experience",
        "Converting the story into operating priorities.", "Team synthesis",
    )
    d = reviewed_delivered(df)
    late = d[d["is_late"] == True]
    on_time = d[d["is_late"] == False]

    def promise_body():
        c1, c2, c3 = st.columns(3)
        c1.metric("On-time negative rate", f"{on_time['is_negative'].mean() * 100:.1f}%", help=f"n = {len(on_time):,}")
        c2.metric("Late negative rate", f"{late['is_negative'].mean() * 100:.1f}%", help=f"n = {len(late):,}")
        c3.metric("Late-order share", f"{len(late) / len(d) * 100:.1f}%", help=f"n = {len(d):,}")
        st.markdown("Use promise-date accuracy, seller handling time, and route performance as the first intervention metrics.")

    section_card(
        "1 · Protect the delivery promise", "Make promise-date accuracy the primary customer-experience control.", promise_body,
        explanation="Late orders are a small share of deliveries but create a disproportionate share of negative reviews.",
        source="processed_data/master_orders.csv", analyst="Yash Arabhavi", report_key="Delivery promise",
        key_suffix="recommend-promise",
    )

    def handling_body():
        st.markdown("Create handling-time SLAs and coach the 77 flagged sellers starting with the slowest-handling quartile. Transit time is courier-controlled and is not a seller lever.")

    section_card(
        "2 · Reduce seller handling time", "Seller-controlled preparation time is a stronger lever than freight pricing.", handling_body,
        explanation=(
            "Sahib's report (Seller Behaviour Drivers) finds handling time has by far the largest, most significant effect among four tested seller behaviours. "
            "Freight ratio shows no reliable independent effect once handling time is controlled for. Transit time is excluded here — it is courier-controlled, not seller-controlled."
        ),
        source="processed_data/master_orders.csv + analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf",
        analyst="Sahib Randhawa", report_key="Seller behaviour", key_suffix="recommend-handling",
    )

    section_card(
        "3 · Target concentrated seller damage", "Intervene with a ranked seller list instead of a blanket marketplace crackdown.",
        lambda: st.markdown("Prioritise sellers using negative rate, reviewed order count, GMV exposure, late rate, and estimated avoidable damage. Keep minimum-volume thresholds visible."),
        explanation="Seller concentration supports targeted coaching and monitoring rather than a blanket seller policy.",
        source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
        analyst="Kannan S", report_key="Seller performance", key_suffix="recommend-sellers",
    )

    section_card(
        "4 · Audit multi-seller shipment tracking", "Do not trust the order-level late rate for multi-seller orders until seller legs are measured separately.",
        lambda: st.markdown("Start with a manual sample audit, then investigate seller-leg tracking. Treat the second-parcel explanation as a hypothesis, not a confirmed cause."),
        explanation="Multi-seller tracking is a measurement-quality action before it is a performance intervention.",
        source="processed_data/master_orders.csv + processed_data/order_items_agg.csv",
        analyst="Team synthesis", key_suffix="recommend-multi",
    )

    section_card(
        "5 · Prioritise worst-performing categories and routes", "Target the states and routes with the highest late-delivery rates, and the categories with the highest bad-review rates.",
        lambda: st.markdown(
            "Regional logistics (Anushka): AL (21.4% late), MA (17.4%), SE (15.2%) are the highest-risk states. "
            "PR→AL (32.6% late) and SP→MA (19.5%, 493 orders) are the worst routes combining late-delivery rate with meaningful volume. "
            "Seller performance (Kannan): office furniture, bed bath table, and furniture decor are the worst categories by bad-review rate (15–21%). "
            "Intervene in these areas before expanding volume through them."
        ),
        explanation=(
            "Anushka's Regional Logistics report identifies specific states (AL, MA, SE) and routes (PR→AL, RJ→CE, SP→AL, SP→MA) "
            "as late-delivery hotspots correlated with lower review scores. "
            "Kannan's Seller Performance report identifies the worst product categories by bad-review rate."
        ),
        source="processed_data/master_orders.csv + processed_data/customers.csv + processed_data/sellers.csv",
        analyst="Anushka / Kannan S", report_key="Regional logistics", key_suffix="recommend-growth",
    )

    def final_body():
        st.markdown(
            "Invest first in promise-date accuracy and seller handling-time reduction. "
            "Then target concentrated seller, route, and category risk. Treat freight pricing "
            "and payment changes as secondary experiments rather than primary satisfaction levers."
        )
        st.markdown(
            "_Data note: handling-time analysis contains impossible negative source values. "
            "Validate or exclude those timestamps before operationalising this view._"
        )

    section_card(
        "6 · Avoid weak primary levers", "Price and freight ratio have small, real effects — but not large enough to lead the intervention budget.",
        final_body,
        explanation=(
            "Ashwanth's Product & Pricing report finds price (r=0.048) and freight ratio (r=0.012) both statistically significant on on-time orders, "
            "but the effect sizes are small. Sahib's report confirms freight ratio shows no reliable independent effect at the seller level once handling time is controlled for. "
            "Operational fixes (delivery promise, handling time) are the primary levers."
        ),
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V / Sahib Randhawa", report_key="Seller behaviour", key_suffix="recommend-final",
    )


# --------------------------------------------------------------------------
# App shell
# --------------------------------------------------------------------------

def render_dashboard():
    apply_theme()
    df = load_master()
    if df.empty:
        st.error("Processed data not found. Run `python3 preprocess.py` from the project root first.")
        return

    st.markdown(
        '<div class="dashboard-brand">'
        '<span class="team">A Visual Study of E-Commerce Orders, Delivery & Customer Satisfaction · Team 2</span></div>',
        unsafe_allow_html=True,
    )

    tab_labels = [
        "Introduction", "Delivery performance", "Regional logistics",
        "Seller performance", "Seller behaviour drivers", "Product and pricing",
        "Recommendations",
    ]
    selected = st.segmented_control("Story", tab_labels, default=tab_labels[0], label_visibility="collapsed", width="stretch")

    renderers = {
        tab_labels[0]: render_introduction,
        tab_labels[1]: render_delivery,
        tab_labels[2]: render_regions,
        tab_labels[3]: render_sellers,
        tab_labels[4]: render_seller_behaviour,
        tab_labels[5]: render_products,
        tab_labels[6]: render_recommendations,
    }
    renderers[selected](df)


if __name__ == "__main__":
    render_dashboard()