import os

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


DATA_DIR = "processed_data"
REPORTS = {
    "Delivery promise": ("Yash Arabhavi", "analysis/Yash/Delivery_Performance_Report.pdf"),
    "Seller performance": ("Kannan S", "analysis/Kannan/Seller_Performance_Report.pdf"),
    "Regional logistics": ("Anushka", "analysis/Anushka/Regional_Logistics_Report.pdf"),
    "Product portfolio": ("Ashwanth V", "analysis/Ashwanth/Product_Pricing_Analysis.pdf"),
    "Recommendations": ("Sahib Randhawa", "analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf"),
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
        html, body, .stApp { background: #eef2f7; color: #16233a; }
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
            background: #0f172a; color: #ffffff; }

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
        .sec-explain { color:#475569; font-size: 13px; line-height:1.5; margin: 14px 0 4px;
            padding-top: 12px; border-top: 1px solid #eef2f7; }
        .sec-explain strong { color:#0f172a; }
        .sec-caption { color:#94a3b8; font-size: 11.5px; margin-top: 4px; }
        [data-testid="stPopover"] > button,
        [data-testid="stPopover"] > button p,
        [data-testid="stPopover"] > button span { color:#64748b !important; font-size:10px !important;
            font-weight:600; line-height:1.2; padding:0 !important; min-height:0 !important;
            min-width:0 !important; width:auto !important; background:transparent !important;
            border:none !important; box-shadow:none !important; }
        [data-testid="stPopover"] > button { color:#2563eb !important; }
        [data-testid="stPopover"] > button:hover,
        [data-testid="stPopover"] > button:focus { color:#1d4ed8 !important; text-decoration:underline;
            outline:none !important; }
        .decision { background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706; color: #78350f;
            padding: 16px 18px; border-radius: 10px; margin: 4px 0 16px; line-height: 1.6; font-size: 14px; }
        .decision strong { color:#78350f; }

        [data-testid="stMetric"] { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; }
        [data-testid="stMetricValue"] { font-size: 22px; }
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
            with st.popover("ⓘ Source & method"):
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
            explanation_column, source_column = st.columns([5, 0.8])
            with explanation_column:
                st.markdown(f'<div class="sec-explain"><strong>What this shows:</strong> {explanation}</div>', unsafe_allow_html=True)
            with source_column:
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


# --------------------------------------------------------------------------
# Chart builders — return alt.Chart objects, never render directly
# --------------------------------------------------------------------------

def bar_chart_obj(frame, x, y, color="#2563eb", sort="-y"):
    return alt.Chart(frame).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X(f"{x}:N", sort=sort, title=None),
        y=alt.Y(f"{y}:Q", title=None),
        color=alt.value(color),
        tooltip=[alt.Tooltip(f"{x}:N", title=x), alt.Tooltip(f"{y}:Q", title=y, format=".1f")],
    ).properties(height=290)


def line_chart_obj(frame, x, y_columns, colors=None):
    values = frame.melt(id_vars=[x], value_vars=y_columns, var_name="Metric", value_name="Value")
    return alt.Chart(values).mark_line(point=True).encode(
        x=alt.X(f"{x}:O", title=None),
        y=alt.Y("Value:Q", title=None),
        color=alt.Color("Metric:N", scale=alt.Scale(range=colors or ["#0891b2", "#e11d48"])),
        tooltip=[alt.Tooltip(f"{x}:O", title=x), alt.Tooltip("Metric:N"), alt.Tooltip("Value:Q", format=".1f")],
    ).properties(height=290)


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
        ).properties(height=320)
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
        "Delivery promise", "Does Missing the Promise Hurt More Than Slow Delivery?",
        "Being slow gradually erodes satisfaction; breaking the promised date creates the sharpest customer penalty.",
        "Yash Arabhavi",
    )
    d = reviewed_delivered(df)
    on_time, late = d[d["is_late"] == False], d[d["is_late"] == True]

    # Section 1 — the promise cliff
    cliff = pd.DataFrame({
        "Delivery status": ["On time", "Late"],
        "Negative rate": [on_time["is_negative"].mean() * 100, late["is_negative"].mean() * 100 if len(late) else 0],
    })

    def cliff_body():
        show(bar_chart_obj(cliff, "Delivery status", "Negative rate", "#e11d48"))
        st.markdown(f'<div class="sec-caption">On time n={len(on_time):,} · Late n={len(late):,}</div>', unsafe_allow_html=True)

    section_card(
        "The promise cliff", "Negative-review rate by delivery status.", cliff_body,
        explanation="The promised date is the sharp boundary where satisfaction drops — not a gradual penalty for taking longer.",
        source="processed_data/master_orders.csv", analyst="Yash Arabhavi", report_key="Delivery promise",
        takeaway=(
            f"On-time orders are {on_time['is_negative'].mean() * 100:.1f}% negative; "
            f"late orders are {late['is_negative'].mean() * 100:.1f}% negative." if len(late) else "No late orders are available."
        ),
        key_suffix="delivery-cliff",
    )

    # Section 2 — slow vs broken promise
    d["delivery bucket"] = pd.cut(d["delivery_days"], [0, 7, 14, 21, 30, 45, 60, np.inf],
                                   labels=["≤7d", "8–14d", "15–21d", "22–30d", "31–45d", "46–60d", "61+d"])
    slow = rate_table(d[d["is_late"] == False], "delivery bucket", "Duration")
    d["late bucket"] = pd.cut(d["delay_days"], [0, 3, 7, 15, 30, np.inf],
                               labels=["0–3d late", "3–7d late", "7–15d late", "15–30d late", "30+d late"])
    broken = rate_table(d[d["is_late"] == True], "late bucket", "Lateness")
    slope_data = pd.concat([
        slow.rename(columns={"Duration": "Bucket"})[["Bucket", "Negative rate"]].assign(Series="Delivery duration when on time"),
        broken.rename(columns={"Lateness": "Bucket"})[["Bucket", "Negative rate"]].assign(Series="Days late after promise"),
    ], ignore_index=True)

    def slope_body():
        chart = alt.Chart(slope_data).mark_line(point=True).encode(
            x=alt.X("Bucket:N", sort=None, title="Duration bucket"),
            y=alt.Y("Negative rate:Q", title="Negative-review rate (%)"),
            color=alt.Color("Series:N", scale=alt.Scale(range=["#0891b2", "#e11d48"])),
            tooltip=["Series:N", "Bucket:N", alt.Tooltip("Negative rate:Q", format=".1f")],
        ).properties(height=320)
        show(chart)

    section_card(
        "Slow versus broken promise",
        "Absolute delivery duration among on-time orders, compared with lateness duration among late orders.",
        slope_body,
        explanation="Slow delivery erodes satisfaction gradually; breaking the promise creates a much steeper increase.",
        source="processed_data/master_orders.csv + analysis/Yash/outputs/q1_delay_buckets.csv + "
               "analysis/Yash/outputs/q2_speed_on_time.csv + analysis/Yash/outputs/q2_lateness.csv",
        analyst="Yash Arabhavi", report_key="Delivery promise", key_suffix="delivery-speed",
    )

    # Section 3 — on-time vs late penalty + data note folded in
    speed = d.copy()
    speed["promise group"] = np.where(speed["is_late"], "Late", "On time")
    two_by_two = speed.groupby("promise group", observed=True).agg(Orders=("order_id", "count"), Negative=("is_negative", "mean")).reset_index()
    two_by_two["Negative rate"] = two_by_two.pop("Negative") * 100

    def penalty_body():
        show(bar_chart_obj(two_by_two, "promise group", "Negative rate", "#f97316"))
        st.markdown(
            '<div class="sec-caption">Extreme timing buckets contain flagged timestamp anomalies and should not be read as proven causal effects.</div>',
            unsafe_allow_html=True,
        )

    section_card(
        "On-time versus late: the customer penalty",
        "Even slow-but-on-time orders outperform fast orders that break the promised date.",
        penalty_body,
        explanation="Meeting the promised date matters more to customers than raw delivery speed.",
        source="analysis/Yash/outputs/q2_two_by_two.csv", analyst="Yash Arabhavi", report_key="Delivery promise",
        key_suffix="delivery-two-by-two",
    )

    # Section 4 — multi-seller teaser
    multi = d.groupby("is_multi_seller").agg(Orders=("order_id", "count"), Late_rate=("is_late", "mean"), Negative_rate=("is_negative", "mean")).reset_index()
    multi["Order type"] = multi["is_multi_seller"].map({False: "Single-seller", True: "Multi-seller"})
    multi[["Late_rate", "Negative_rate"]] *= 100
    multi = multi[["Order type", "Orders", "Late_rate", "Negative_rate"]].rename(columns={"Late_rate": "Late rate", "Negative_rate": "Negative rate"}).round(1)
    single_n = int(multi.loc[multi["Order type"] == "Single-seller", "Orders"].iloc[0]) if (multi["Order type"] == "Single-seller").any() else 0
    multi_n = int(multi.loc[multi["Order type"] == "Multi-seller", "Orders"].iloc[0]) if (multi["Order type"] == "Multi-seller").any() else 0

    def multi_body():
        show(line_chart_obj(multi, "Order type", ["Late rate", "Negative rate"], ["#0891b2", "#e11d48"]))
        st.markdown(f'<div class="sec-caption">Single-seller n={single_n:,} · Multi-seller n={multi_n:,}</div>', unsafe_allow_html=True)

    section_card(
        "Multi-seller anomaly",
        "Order-level tracking records a single late flag, so multi-seller orders need a separate audit.",
        multi_body,
        explanation="Multi-seller orders show a measurement gap between recorded lateness and actual customer experience — explored fully on the next tab.",
        source="processed_data/master_orders.csv + processed_data/order_items_agg.csv",
        analyst="Yash Arabhavi / Team synthesis", key_suffix="delivery-multi",
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
        ).properties(height=310)
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
# Tab 4 — Seller Damage
# --------------------------------------------------------------------------

def render_sellers(df):
    page_header(
        "Seller performance", "Which Sellers Create Avoidable Customer Damage?",
        "Concentrate intervention where negative experiences and commercial exposure overlap.", "Kannan S",
    )
    d = reviewed_delivered(df)

    sellers = rate_table(d, "primary_seller_id", "Seller ID")
    sellers = sellers[sellers["Orders"] >= 20].sort_values("Negative rate", ascending=False)
    sellers["Cumulative negative share"] = (sellers["Orders"] * sellers["Negative rate"] / 100).cumsum() / (sellers["Orders"] * sellers["Negative rate"] / 100).sum() * 100
    sellers["Cumulative order share"] = sellers["Orders"].cumsum() / sellers["Orders"].sum() * 100
    concentration = sellers.reset_index(drop=True).reset_index().rename(columns={"index": "Seller rank"})
    concentration["Seller rank"] += 1

    def concentration_body():
        line_values = concentration.melt(id_vars=["Seller rank"], value_vars=["Cumulative negative share", "Cumulative order share"], var_name="Metric", value_name="Share")
        chart = alt.Chart(line_values).mark_line().encode(
            x=alt.X("Seller rank:Q", title="Seller rank"), y=alt.Y("Share:Q", title="Cumulative share (%)"),
            color=alt.Color("Metric:N", scale=alt.Scale(range=["#e11d48", "#0891b2"])),
            tooltip=["Seller rank:Q", "Metric:N", "Share:Q"],
        ).properties(height=320)
        show(chart)

    section_card(
        "Seller risk concentration",
        "Sellers with fewer than 20 reviewed orders are excluded from ranking.",
        concentration_body,
        explanation="Negative reviews are concentrated among a smaller seller group, making targeted intervention more practical than a marketplace-wide crackdown.",
        source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
        analyst="Kannan S", report_key="Seller performance",
        takeaway="The top 5% of sellers by negative-order contribution account for a disproportionate share of all negative reviews.",
        key_suffix="seller-concentration",
    )

    sellers["Risk"] = np.select(
        [sellers["Negative rate"] > d["is_negative"].mean() * 100, sellers["GMV"] > sellers["GMV"].median()],
        ["Experience risk", "Commercial exposure"], default="Monitor",
    )
    section_card(
        "High-value intervention list",
        "Highest negative-rate sellers, ranked with GMV exposure in mind.",
        lambda: show(bar_chart_obj(sellers.head(15), "Seller ID", "Negative rate", "#ec4899")),
        explanation="Rank sellers only above a minimum reviewed-order threshold, and pair negative rate with GMV before assigning an action.",
        source="processed_data/master_orders.csv + analysis/Kannan/Seller_Performance_Analysis.ipynb",
        analyst="Kannan S", report_key="Seller performance", key_suffix="seller-watchlist",
    )


# --------------------------------------------------------------------------
# Tab 5 — Route Risk
# --------------------------------------------------------------------------

def render_regions(df):
    page_header(
        "Regional logistics", "Where Do Delivery Routes Fail Customers?",
        "Always read rate and volume together: a high rate with low volume is a signal, not a mandate.", "Anushka",
    )
    d = reviewed_delivered(df)

    states = rate_table(d, "customer_state", "Customer state").query("Orders >= 50").sort_values("Negative rate", ascending=False)

    def states_body():
        show(bar_chart_obj(states.head(12), "Customer state", "Negative rate", "#ec4899"))
        show(bar_chart_obj(states.sort_values("Orders", ascending=False).head(12), "Customer state", "Orders", "#0891b2"))

    section_card(
        "Customer-state risk", "States with at least 50 reviewed orders: negative rate, then order volume.", states_body,
        explanation="Regional risk is meaningful only when the negative rate is read alongside the number of reviewed orders.",
        source="processed_data/master_orders.csv + processed_data/customers.csv", analyst="Anushka",
        report_key="Regional logistics", key_suffix="region-states",
    )

    routes = d.groupby(["seller_state", "customer_state"]).agg(
        Orders=("order_id", "count"), Negative_rate=("is_negative", "mean"), Median_days=("delivery_days", "median"), Late_rate=("is_late", "mean")
    ).reset_index()
    routes["Negative rate"] = (routes.pop("Negative_rate") * 100).round(1)
    routes["Late rate"] = (routes.pop("Late_rate") * 100).round(1)
    routes["Median delivery days"] = routes.pop("Median_days").round(1)
    route_view = routes.query("Orders >= 30").sort_values("Negative rate", ascending=False).head(15).copy()
    route_view["Route"] = route_view["seller_state"] + " → " + route_view["customer_state"]

    def routes_body():
        show(bar_chart_obj(route_view, "Route", "Negative rate", "#f97316"))
        heat = routes.query("Orders >= 30").pivot(index="seller_state", columns="customer_state", values="Negative rate").fillna(0).reset_index().melt("seller_state", var_name="customer_state", value_name="Negative rate")
        heatmap = alt.Chart(heat).mark_rect().encode(
            x=alt.X("customer_state:N", title="Customer state"), y=alt.Y("seller_state:N", title="Seller state"),
            color=alt.Color("Negative rate:Q", scale=alt.Scale(range=["#fce7f3", "#ec4899", "#9d174d"])),
            tooltip=["seller_state:N", "customer_state:N", alt.Tooltip("Negative rate:Q", format=".1f")],
        ).properties(height=340)
        show(heatmap)

    section_card(
        "Seller-state to customer-state routes",
        "Worst routes by negative rate, then the full route heatmap. Routes below 30 orders are suppressed.",
        routes_body,
        explanation="A route heatmap highlights where seller origin and customer destination combine into recurring experience risk.",
        source="processed_data/master_orders.csv + processed_data/sellers.csv + processed_data/customers.csv",
        analyst="Anushka", report_key="Regional logistics",
        takeaway="RJ shows an 18.26% negative rate; SP carries the largest volume (40,273 orders) at a 10.63% negative rate.",
        key_suffix="region-routes",
    )


# --------------------------------------------------------------------------
# Tab 6 — Product Risk
# --------------------------------------------------------------------------

def render_products(df):
    page_header(
        "Product portfolio", "Which Products Generate Revenue but Disappoint Customers?",
        "Find categories where growth exposure and customer-experience risk meet.", "Ashwanth V",
    )
    d = reviewed_delivered(df)
    baseline = d["is_negative"].mean() * 100

    categories = rate_table(d, "primary_category", "Category").sort_values("GMV", ascending=False)
    categories["Priority"] = np.select(
        [categories["Negative rate"] > baseline, categories["GMV"] > categories["GMV"].median()],
        ["Experience risk", "Commercial exposure"], default="Protect / monitor",
    )

    def quadrant_body():
        chart = alt.Chart(categories.head(30)).mark_circle(opacity=0.85).encode(
            x=alt.X("GMV:Q", title="GMV (R$)"), y=alt.Y("Negative rate:Q", title="Negative-review rate (%)"),
            size=alt.Size("Orders:Q", title="Orders"),
            color=alt.Color("Priority:N", scale=alt.Scale(range=["#e11d48", "#059669", "#f59e0b"])),
            tooltip=["Category:N", "Orders:Q", "GMV:Q", "Negative rate:Q", "Priority:N"],
        ).properties(height=340)
        show(chart)

    section_card(
        "Growth versus experience quadrant",
        "GMV is commercial exposure; negative rate is experience risk. The horizontal reference is the filtered baseline.",
        quadrant_body,
        explanation="Categories with substantial GMV and above-baseline negative rates are the clearest portfolio intervention zone.",
        source="processed_data/master_orders.csv + processed_data/order_items.csv", analyst="Ashwanth V",
        report_key="Product portfolio",
        takeaway=f"Office furniture stands out: 1,244 orders, R$265k GMV, and a 25.45% negative rate — nearly double the {baseline:.1f}% baseline.",
        key_suffix="product-quadrant",
    )

    section_card(
        "Top categories by GMV",
        "A sorted portfolio view keeps revenue and negative rate visible together.",
        lambda: st.bar_chart(numeric_chart(categories.head(15).set_index("Category"), ["GMV"]), color="#059669"),
        explanation="Revenue ranking keeps commercial scale visible while the quadrant above identifies where experience risk is unusually high.",
        source="processed_data/master_orders.csv + processed_data/order_items.csv", analyst="Ashwanth V",
        report_key="Product portfolio", key_suffix="product-revenue",
    )

    driver_rows = []
    for column in ["delivery_days", "transit_days", "delay_days", "handling_days", "total_price", "freight_ratio", "max_installments"]:
        if column in d and d[column].notna().sum() > 10:
            driver_rows.append({"Variable": column, "Association with negative review": d[[column, "is_negative"]].corr(numeric_only=True).iloc[0, 1]})
    drivers = pd.DataFrame(driver_rows).sort_values("Association with negative review", key=lambda x: x.abs(), ascending=False)

    section_card(
        "Driver signals",
        "Delivery and transit variables versus price, freight, and payment variables.",
        lambda: show(bar_chart_obj(drivers, "Variable", "Association with negative review", "#8b5cf6")),
        explanation="Delivery execution has a much stronger association with negative reviews than price, freight ratio, or payment variables. These are associations, not proof of causation.",
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V / Team synthesis", report_key="Product portfolio", key_suffix="product-drivers",
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

    rows = []
    for label, column, bins, labels in [
        ("Handling time", "handling_days", [-np.inf, 1, 3, 7, 14, np.inf], ["≤1d", "1–3d", "3–7d", "7–14d", "14+d"]),
        ("Transit time", "transit_days", [-np.inf, 5, 10, 21, 31, np.inf], ["≤5d", "5–10d", "10–21d", "21–31d", "31+d"]),
        ("Freight ratio", "freight_ratio", [-np.inf, .1, .3, 1, np.inf], ["<10%", "10–30%", "30–100%", ">100%"]),
    ]:
        buckets = pd.cut(d[column], bins=bins, labels=labels)
        grouped = d.assign(Bucket=buckets).groupby("Bucket", observed=True)["is_negative"].agg(["count", "mean"]).reset_index()
        grouped = grouped[grouped["count"] >= 50]
        if not grouped.empty:
            rows.append({
                "Driver": label, "Best rate": grouped["mean"].min() * 100, "Worst rate": grouped["mean"].max() * 100,
                "Spread": (grouped["mean"].max() - grouped["mean"].min()) * 100,
            })
    driver_spread = pd.DataFrame(rows).sort_values("Spread", ascending=False) if rows else pd.DataFrame()

    def handling_body():
        if not driver_spread.empty:
            show(bar_chart_obj(driver_spread, "Driver", "Spread", "#f59e0b"))
            st.markdown(
                '<div class="sec-caption">' +
                " · ".join(f"{row['Driver']}: {row['Best rate']:.1f}% → {row['Worst rate']:.1f}%" for _, row in driver_spread.iterrows()) +
                "</div>", unsafe_allow_html=True,
            )
        st.markdown("Create handling-time SLAs, coach sellers with repeated delays, and validate the 1,359 negative handling-time values before operational use.")

    section_card(
        "2 · Reduce seller handling time", "Seller-controlled preparation time is a stronger lever than freight pricing.", handling_body,
        explanation="Handling time is seller-controlled, but impossible negative timestamps must be corrected before operational use.",
        source="processed_data/master_orders.csv + analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf",
        analyst="Sahib Randhawa", report_key="Recommendations", key_suffix="recommend-handling",
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
        "5 · Focus category and route investment", "Pair commercial exposure with experience risk so growth investment does not amplify avoidable dissatisfaction.",
        lambda: st.markdown("Prioritise high-GMV/high-negative categories and routes with both meaningful volume and elevated negative rates. Protect high-GMV/low-negative categories."),
        explanation="Use the category quadrant and route risk charts to direct investment toward high-exposure, high-risk areas.",
        source="processed_data/master_orders.csv + processed_data/products.csv + processed_data/customers.csv + processed_data/sellers.csv",
        analyst="Team synthesis", key_suffix="recommend-growth",
    )

    def final_body():
        st.markdown(
            '<div class="decision"><strong>Final recommendation:</strong> invest first in promise-date accuracy and seller '
            'handling-time reduction. Then target concentrated seller, route, and category risk. Treat freight pricing '
            'and payment changes as secondary experiments rather than primary satisfaction levers.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sec-caption">Data note: handling-time analysis contains impossible negative source values. '
            'Validate or exclude those timestamps before operationalising this view.</div>', unsafe_allow_html=True,
        )

    section_card(
        "6 · Avoid weak primary levers", "Price, freight ratio, payment type, and instalments should not lead the intervention budget.",
        final_body,
        explanation="The strongest measured gaps are operational, so price and payment changes should remain secondary experiments.",
        source="processed_data/master_orders.csv + processed_data/products.csv",
        analyst="Ashwanth V / Sahib Randhawa", report_key="Recommendations", key_suffix="recommend-final",
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
        "Trust & Growth", "Promise vs Speed", "Multi-Seller Blind Spot",
        "Seller Damage", "Route Risk", "Product Risk", "Recommendations",
    ]
    selected = st.segmented_control("Story", tab_labels, default=tab_labels[0], label_visibility="collapsed", width="stretch")

    renderers = {
        tab_labels[0]: render_overview,
        tab_labels[1]: render_delivery,
        tab_labels[2]: render_multi_seller,
        tab_labels[3]: render_sellers,
        tab_labels[4]: render_regions,
        tab_labels[5]: render_products,
        tab_labels[6]: render_recommendations,
    }
    renderers[selected](df)


if __name__ == "__main__":
    render_dashboard()