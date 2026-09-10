import os

import numpy as np
import pandas as pd
import streamlit as st


DATA_DIR = "processed_data"
REPORTS = {
    "Delivery promise": ("Yash Arabhavi", "analysis/Yash/Delivery_Performance_Report.pdf"),
    "Seller performance": ("Kannan S", "analysis/Kannan/Seller_Performance_Report.pdf"),
    "Regional logistics": ("Anushka", "analysis/Anushka/Regional_Logistics_Report.pdf"),
    "Product portfolio": ("Ashwanth V", "analysis/Ashwanth/Product_Pricing_Analysis.pdf"),
    "Recommendations": ("Sahib Randhawa", "analysis/Sahib/Sahib_Seller_Behaviour_Investment_Report.pdf"),
}


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


def apply_light_theme():
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        .stApp { background: #f6f8fb; color: #172033; }
        .stAppViewContainer .main .block-container { padding-top: 0.75rem !important; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
        .dashboard-brand { color: #627d98; font-size: 17px; font-weight: 600; letter-spacing: 0.1px; margin: 0 0 10px; }
        .dashboard-team { color: #829ab1; font-size: 14px; font-weight: 500; margin-left: 8px; }
        [data-testid="stMetric"] { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; }
        [data-testid="stSegmentedControl"] { width: 100%; background: #e8eef5; border: 1px solid #cbd5e1; border-radius: 12px; padding: 6px; }
        [data-testid="stSegmentedControl"] button { flex: 1 1 0; min-height: 54px; padding: 11px 18px; border-radius: 8px; background: transparent; color: #243b53; font-size: 15px; font-weight: 800; white-space: nowrap; }
        [data-testid="stSegmentedControl"] button p, [data-testid="stSegmentedControl"] button span { color: inherit; font-size: inherit; font-weight: 800; }
        [data-testid="stSegmentedControl"] button[aria-checked="true"], [data-testid="stSegmentedControl"] button[aria-pressed="true"] { background: #1d4ed8; color: #ffffff; box-shadow: 0 2px 6px rgba(29, 78, 216, 0.25); }
        .dash-hero { background: #ffffff; border: 1px solid #dbe4ef; border-left: 5px solid #2563eb; border-radius: 12px; padding: 24px 28px; margin: 4px 0 20px; }
        .dash-hero h1 { color: #102a43; margin: 0 0 6px; font-size: 30px; }
        .dash-hero p { color: #52606d; margin: 0; line-height: 1.55; }
        .section-title { color: #102a43; font-size: 19px; font-weight: 750; margin: 22px 0 2px; }
        .section-subtext { color: #627d98; font-size: 13px; margin: 0 0 9px; }
        .takeaway { background: #eff6ff; border-left: 4px solid #2563eb; color: #1e3a5f; padding: 11px 14px; border-radius: 0 8px 8px 0; margin: 10px 0 14px; font-size: 14px; }
        .decision { background: #fff7ed; border-left: 4px solid #f59e0b; color: #78350f; padding: 16px 18px; border-radius: 0 8px 8px 0; margin: 16px 0; line-height: 1.6; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def source_info(source, analyst, report_key=None, key_suffix=""):
    with st.expander("ⓘ Source, method and analysis", expanded=False):
        st.caption(f"Source / dataset file: `{source}`")
        st.caption(f"Analysed by: {analyst}")
        if report_key and report_key in REPORTS:
            report_owner, report_path = REPORTS[report_key]
            st.caption(f"Analysis report: {report_owner}")
            if os.path.exists(report_path):
                with open(report_path, "rb") as report_file:
                    st.download_button(
                        "Download analysis report",
                        report_file.read(),
                        file_name=os.path.basename(report_path),
                        mime="application/pdf",
                        key=f"report-{report_key}-{key_suffix}",
                    )
            else:
                st.caption(f"Report path: `{report_path}`")


def page_header(title, subtitle, analyst="Team synthesis"):
    st.markdown(
        f'<div class="dash-hero"><h1>{title}</h1><p>{subtitle}</p><p style="margin-top:8px;font-size:12px;color:#829ab1">Analysed by {analyst} · filtered delivered orders with a review unless stated otherwise</p></div>',
        unsafe_allow_html=True,
    )


def section(title, subtext, source, analyst, report_key=None, takeaway=None):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-subtext">{subtext}</div>', unsafe_allow_html=True)
    if takeaway:
        st.markdown(f'<div class="takeaway">{takeaway}</div>', unsafe_allow_html=True)
    source_info(source, analyst, report_key, key_suffix=title)


def reviewed_delivered(df):
    return df[(df["order_status"] == "delivered") & df["is_negative"].notna()].copy()


def rate_table(frame, group, label):
    result = frame.groupby(group, dropna=False).agg(
        Orders=("order_id", "count"),
        Negative=("is_negative", "mean"),
        GMV=("total_price", "sum"),
    ).reset_index().rename(columns={group: label})
    result["Negative rate"] = (
        pd.to_numeric(result.pop("Negative"), errors="coerce") * 100
    ).round(1)
    result["GMV"] = pd.to_numeric(result["GMV"], errors="coerce").round(0)
    return result


def numeric_chart(frame, columns):
    """Return a chart frame with a guaranteed numeric dtype."""
    chart = frame.loc[:, columns].copy()
    for column in columns:
        chart[column] = pd.to_numeric(chart[column], errors="coerce").fillna(0.0).astype(float)
    return chart


def render_overview(df):
    page_header("Can We Grow Without Breaking Customer Trust?", "Where can we grow sales, and where must we intervene before customer satisfaction deteriorates?")
    d = reviewed_delivered(df)
    if d.empty:
        st.warning("No reviewed delivered orders are available.")
        return
    baseline = d["is_negative"].mean() * 100
    late = d[d["is_late"] == True]
    on_time = d[d["is_late"] == False]
    late_share = len(late) / len(d) * 100
    negative_share = late["is_negative"].sum() / d["is_negative"].sum() * 100 if d["is_negative"].sum() else 0
    section("Risk summary", "Late delivery is a small share of reviewed deliveries but a much larger share of negative reviews.", "processed_data/master_orders.csv", "Team synthesis", takeaway=f"Late orders are {late_share:.1f}% of deliveries. They produce {negative_share:.1f}% of all negative reviews.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviewed orders", f"{len(d):,}", help="n = reviewed delivered orders")
    c2.metric("Negative rate", f"{baseline:.1f}%", help="Reviews scored 1 or 2")
    c3.metric("Late share", f"{late_share:.1f}%", help="Late reviewed delivered orders")
    c4.metric("Late negative rate", f"{late['is_negative'].mean() * 100:.1f}%" if len(late) else "n/a")
    risk = pd.DataFrame({"Group": ["On time", "Late"], "Negative rate": [on_time["is_negative"].mean() * 100, late["is_negative"].mean() * 100 if len(late) else 0], "Orders": [len(on_time), len(late)]})
    st.bar_chart(numeric_chart(risk.set_index("Group"), ["Negative rate"]), color="#2563eb")
    section("Growth versus experience", "Categories with both material GMV and above-baseline negative rates are the clearest intervention zone.", "processed_data/master_orders.csv", "Ashwanth V / Team synthesis", "Product portfolio")
    category = rate_table(d, "primary_category", "Category").sort_values("GMV", ascending=False).head(15)
    category["GMV (R$) "] = category.pop("GMV")
    st.dataframe(category, use_container_width=True, hide_index=True)
    section("Monthly context", "Negative-review rate and late-delivery rate show whether the experience risk is moving with delivery execution.", "processed_data/master_orders.csv", "Team synthesis")
    monthly = d.assign(Month=d["order_purchase_timestamp"].dt.to_period("M").astype(str)).groupby("Month").agg(Negative_rate=("is_negative", "mean"), Late_rate=("is_late", "mean")) * 100
    st.line_chart(numeric_chart(monthly, ["Negative_rate", "Late_rate"]))
    st.markdown('<div class="decision"><strong>Leadership signal:</strong> protect the promise date first, then target the sellers, routes, and categories where risk and commercial exposure overlap.</div>', unsafe_allow_html=True)


def render_delivery(df):
    page_header("Does Missing the Promise Hurt More Than Slow Delivery?", "Being slow gradually erodes satisfaction; breaking the promised date creates the sharpest customer penalty.", "Yash Arabhavi")
    d = reviewed_delivered(df)
    on_time, late = d[d["is_late"] == False], d[d["is_late"] == True]
    section("The promise cliff", "Negative-review rate by delivery status, with order count shown beside every rate.", "processed_data/master_orders.csv", "Yash Arabhavi", "Delivery promise", f"On-time orders are {on_time['is_negative'].mean() * 100:.1f}% negative; late orders are {late['is_negative'].mean() * 100:.1f}% negative." if len(late) else "No late orders are available.")
    cliff = pd.DataFrame({"Delivery status": ["On time", "Late"], "Negative rate": [on_time["is_negative"].mean() * 100, late["is_negative"].mean() * 100 if len(late) else 0], "n": [len(on_time), len(late)]})
    st.bar_chart(numeric_chart(cliff.set_index("Delivery status"), ["Negative rate"]), color="#ef4444")
    st.dataframe(cliff, use_container_width=True, hide_index=True)
    section("Slow versus broken promise", "Compare absolute delivery duration among on-time orders with lateness duration among late orders.", "processed_data/master_orders.csv", "Yash Arabhavi", "Delivery promise")
    left, right = st.columns(2)
    with left:
        st.markdown("**On-time delivery duration**")
        d["delivery bucket"] = pd.cut(d["delivery_days"], [0, 7, 14, 21, 30, 45, 60, np.inf], labels=["≤7d", "8–14d", "15–21d", "22–30d", "31–45d", "46–60d", "61+d"])
        slow = rate_table(d[d["is_late"] == False], "delivery bucket", "Duration")
        st.dataframe(slow, use_container_width=True, hide_index=True)
    with right:
        st.markdown("**Late delivery duration**")
        d["late bucket"] = pd.cut(d["delay_days"], [0, 3, 7, 15, 30, np.inf], labels=["0–3d late", "3–7d late", "7–15d late", "15–30d late", "30+d late"])
        broken = rate_table(d[d["is_late"] == True], "late bucket", "Lateness")
        st.dataframe(broken, use_container_width=True, hide_index=True)
    st.warning("Data note: extreme timing buckets contain flagged timestamp anomalies and should not be read as proven causal effects.")
    section("Multi-seller anomaly", "Order-level tracking records a single late flag, so multi-seller orders need a separate audit.", "processed_data/master_orders.csv + processed_data/order_items_agg.csv", "Yash Arabhavi / Team synthesis")
    multi = d.groupby("is_multi_seller").agg(Orders=("order_id", "count"), Late_rate=("is_late", "mean"), Negative_rate=("is_negative", "mean")).reset_index()
    multi["Order type"] = multi["is_multi_seller"].map({False: "Single-seller", True: "Multi-seller"})
    multi[["Late_rate", "Negative_rate"]] *= 100
    multi = multi[["Order type", "Orders", "Late_rate", "Negative_rate"]].rename(columns={"Late_rate": "Late rate", "Negative_rate": "Negative rate"}).round(1)
    st.dataframe(multi, use_container_width=True, hide_index=True)


def render_multi_seller(df):
    page_header("Why Do Multi-Seller Orders Look On-Time but Feel Bad?", "Multi-seller orders may look on-time at order level while the customer still experiences a fragmented delivery.")
    d = reviewed_delivered(df)
    section("The multi-seller blind spot", "The gap between recorded lateness and customer dissatisfaction is the central measurement risk.", "processed_data/master_orders.csv + processed_data/order_items_agg.csv", "Team synthesis", takeaway="A multi-seller order records one shipment event. The second-parcel theory is inferred, not confirmed in the current data.")
    comparison = d.groupby("is_multi_seller").agg(Orders=("order_id", "count"), Late_rate=("is_late", "mean"), Negative_rate=("is_negative", "mean"), GMV=("total_price", "sum")).reset_index()
    comparison["Order type"] = comparison["is_multi_seller"].map({False: "Single-seller", True: "Multi-seller"})
    comparison["Late rate"] = (comparison.pop("Late_rate") * 100).round(1)
    comparison["Negative rate"] = (comparison.pop("Negative_rate") * 100).round(1)
    comparison["GMV (R$)"] = comparison.pop("GMV").round(0)
    st.dataframe(comparison[["Order type", "Orders", "Late rate", "Negative rate", "GMV (R$)"]], use_container_width=True, hide_index=True)
    st.bar_chart(numeric_chart(comparison.set_index("Order type"), ["Late rate", "Negative rate"]), color=["#2563eb", "#ef4444"])
    st.markdown('<div class="decision"><strong>Recommendation:</strong> investigate seller-leg tracking for multi-seller orders, starting with a manual sample audit before using their order-level late rate for performance decisions.</div>', unsafe_allow_html=True)


def render_sellers(df):
    page_header("Which Sellers Create Avoidable Customer Damage?", "Concentrate intervention where negative experiences and commercial exposure overlap.", "Kannan S")
    d = reviewed_delivered(df)
    section("Seller risk concentration", "Every seller rate is paired with reviewed order count and GMV; sellers with fewer than 20 reviewed orders are excluded from ranking.", "processed_data/master_orders.csv", "Kannan S", "Seller performance")
    sellers = rate_table(d, "primary_seller_id", "Seller ID")
    sellers = sellers[sellers["Orders"] >= 20].sort_values("Negative rate", ascending=False)
    st.dataframe(sellers.head(20), use_container_width=True, hide_index=True)
    section("High-value intervention list", "The first rows are sellers with high negative rate and meaningful GMV exposure.", "processed_data/master_orders.csv", "Kannan S", "Seller performance")
    sellers["Risk"] = np.select([sellers["Negative rate"] > d["is_negative"].mean() * 100, sellers["GMV"] > sellers["GMV"].median()], ["Experience risk", "Commercial exposure"], default="Monitor")
    st.dataframe(sellers.head(15), use_container_width=True, hide_index=True)


def render_regions(df):
    page_header("Where Do Delivery Routes Fail Customers?", "Always read rate and volume together: a high rate with low volume is a signal, not a mandate.", "Anushka")
    d = reviewed_delivered(df)
    section("Customer-state risk", "States with at least 50 reviewed orders, ranked by negative-review rate.", "processed_data/master_orders.csv + processed_data/customers.csv", "Anushka", "Regional logistics")
    states = rate_table(d, "customer_state", "Customer state").query("Orders >= 50").sort_values("Negative rate", ascending=False)
    st.dataframe(states, use_container_width=True, hide_index=True)
    section("Seller-state to customer-state routes", "Routes with at least 30 reviewed orders, ranked by negative rate.", "processed_data/master_orders.csv + processed_data/sellers.csv + processed_data/customers.csv", "Anushka", "Regional logistics")
    routes = d.groupby(["seller_state", "customer_state"]).agg(Orders=("order_id", "count"), Negative_rate=("is_negative", "mean"), Median_days=("delivery_days", "median"), Late_rate=("is_late", "mean")).reset_index()
    routes["Negative rate"] = (routes.pop("Negative_rate") * 100).round(1)
    routes["Late rate"] = (routes.pop("Late_rate") * 100).round(1)
    routes["Median delivery days"] = routes.pop("Median_days").round(1)
    st.dataframe(routes.query("Orders >= 30").sort_values("Negative rate", ascending=False).head(20), use_container_width=True, hide_index=True)


def render_products(df):
    page_header("Which Products Generate Revenue but Disappoint Customers?", "Find categories where growth exposure and customer-experience risk meet.", "Ashwanth V")
    d = reviewed_delivered(df)
    baseline = d["is_negative"].mean() * 100
    section("Growth versus experience quadrant", "GMV is the commercial exposure; negative rate is the experience risk. The horizontal reference is the filtered baseline.", "processed_data/master_orders.csv + processed_data/order_items.csv", "Ashwanth V", "Product portfolio", f"Office furniture is a priority when it remains above the {baseline:.1f}% negative-rate baseline with material GMV.")
    categories = rate_table(d, "primary_category", "Category").sort_values("GMV", ascending=False)
    categories["Priority"] = np.select([categories["Negative rate"] > baseline, categories["GMV"] > categories["GMV"].median()], ["Experience risk", "Commercial exposure"], default="Protect / monitor")
    st.dataframe(categories.head(25), use_container_width=True, hide_index=True)
    section("Top categories by GMV", "A sorted portfolio view keeps revenue and negative rate visible together.", "processed_data/master_orders.csv + processed_data/order_items.csv", "Ashwanth V", "Product portfolio")
    st.bar_chart(numeric_chart(categories.head(15).set_index("Category"), ["GMV"]), color="#0f766e")
    section("Driver signals", "Delivery and transit variables are stronger operational signals than price or freight ratio; these are associations, not causation.", "processed_data/master_orders.csv", "Ashwanth V / Team synthesis", "Product portfolio")
    driver_rows = []
    for column in ["delivery_days", "transit_days", "delay_days", "handling_days", "total_price", "freight_ratio", "max_installments"]:
        if column in d and d[column].notna().sum() > 10:
            driver_rows.append({"Variable": column, "Association with negative review": d[[column, "is_negative"]].corr(numeric_only=True).iloc[0, 1]})
    st.dataframe(pd.DataFrame(driver_rows).sort_values("Association with negative review", key=lambda x: x.abs(), ascending=False).round(3), use_container_width=True, hide_index=True)


def render_recommendations(df):
    page_header("Recommendations for Growth Without Breaking Experience", "A single action page that converts the story into operating priorities.", "Team synthesis")
    d = reviewed_delivered(df)
    section("1. Protect the delivery promise", "Make promise-date accuracy the primary customer-experience control.", "processed_data/master_orders.csv", "Yash Arabhavi", "Delivery promise", "Late orders are a small share of deliveries but create a disproportionate share of negative reviews.")
    c1, c2, c3 = st.columns(3)
    late = d[d["is_late"] == True]
    on_time = d[d["is_late"] == False]
    c1.metric("On-time negative rate", f"{on_time['is_negative'].mean() * 100:.1f}%", help=f"n = {len(on_time):,}")
    c2.metric("Late negative rate", f"{late['is_negative'].mean() * 100:.1f}%", help=f"n = {len(late):,}")
    c3.metric("Late-order share", f"{len(late) / len(d) * 100:.1f}%", help=f"n = {len(d):,} reviewed delivered orders")
    st.markdown("Use promise-date accuracy, seller handling time, and route performance as the first intervention dashboard metrics.")

    section("2. Reduce seller handling time", "Seller-controlled preparation time is a stronger operational lever than freight pricing.", "processed_data/master_orders.csv", "Sahib Randhawa", "Recommendations")
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
            rows.append({"Driver": label, "Best bucket": grouped.loc[grouped["mean"].idxmin(), "Bucket"], "Best rate": grouped["mean"].min() * 100, "Worst bucket": grouped.loc[grouped["mean"].idxmax(), "Bucket"], "Worst rate": grouped["mean"].max() * 100, "Spread": (grouped["mean"].max() - grouped["mean"].min()) * 100})
    if rows:
        st.dataframe(pd.DataFrame(rows).sort_values("Spread", ascending=False).round(1), use_container_width=True, hide_index=True)
    st.markdown("Create handling-time SLAs, coach sellers with repeated delays, and validate the 1,359 negative handling-time values before operational use.")

    section("3. Target concentrated seller damage", "Intervene with a ranked seller list instead of applying a blanket marketplace crackdown.", "processed_data/master_orders.csv", "Kannan S", "Seller performance")
    st.markdown("Prioritise sellers using negative rate, reviewed order count, GMV exposure, late rate, and estimated avoidable damage. Keep minimum-volume thresholds visible.")

    section("4. Audit multi-seller shipment tracking", "Do not trust the order-level late rate for multi-seller orders until seller legs are measured separately.", "processed_data/master_orders.csv + processed_data/order_items_agg.csv", "Team synthesis")
    st.markdown("Start with a manual sample audit, then investigate seller-leg tracking. Treat the second-parcel explanation as a hypothesis, not a confirmed cause.")

    section("5. Focus category and route investment", "Pair commercial exposure with experience risk so growth investment does not amplify avoidable dissatisfaction.", "processed_data/master_orders.csv + processed_data/products.csv + processed_data/customers.csv + processed_data/sellers.csv", "Team synthesis")
    st.markdown("Prioritise high-GMV/high-negative categories and routes with both meaningful volume and elevated negative rates. Protect high-GMV/low-negative categories.")

    section("6. Avoid weak primary levers", "Price, freight ratio, payment type, and instalments should not lead the customer-experience intervention budget.", "processed_data/master_orders.csv", "Ashwanth V / Sahib Randhawa", "Recommendations")
    st.markdown('<div class="decision"><strong>Final recommendation:</strong> invest first in promise-date accuracy and seller handling-time reduction. Then target concentrated seller, route, and category risk. Treat freight pricing and payment changes as secondary experiments rather than primary satisfaction levers.</div>', unsafe_allow_html=True)
    st.warning("Data note: handling-time analysis contains impossible negative source values. Validate or exclude those timestamps before operationalising this view.")


def render_dashboard():
    apply_light_theme()
    df = load_master()
    if df.empty:
        st.error("Processed data not found. Run `python3 preprocess.py` from the project root first.")
        return
    st.markdown('<div class="dashboard-brand">A Visual Study of E-Commerce Orders, Delivery &amp; Customer Satisfaction <span class="dashboard-team">· Team 2</span></div>', unsafe_allow_html=True)
    tab_labels = [
        "Trust & Growth",
        "Promise vs Speed",
        "Multi-Seller Blind Spot",
        "Seller Damage",
        "Route Risk",
        "Product Risk",
        "Recommendations",
    ]
    selected = st.segmented_control(
        "Story",
        tab_labels,
        default=tab_labels[0],
        label_visibility="collapsed",
        width="stretch",
    )
    filtered = df

    if selected == tab_labels[0]:
        render_overview(filtered)
    elif selected == tab_labels[1]:
        render_delivery(filtered)
    elif selected == tab_labels[2]:
        render_multi_seller(filtered)
    elif selected == tab_labels[3]:
        render_sellers(filtered)
    elif selected == tab_labels[4]:
        render_regions(filtered)
    elif selected == tab_labels[5]:
        render_products(filtered)
    elif selected == tab_labels[6]:
        render_recommendations(filtered)
