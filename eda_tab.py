import os
import pandas as pd
import numpy as np
import streamlit as st

DATA = "processed_data"

@st.cache_data(show_spinner=False)
def load_master():
    df = pd.read_csv(os.path.join(DATA, "master_orders.csv"), low_memory=False)
    df["is_late"]         = df["is_late"].map({"True": True, "False": False, True: True, False: False})
    df["is_negative"]     = df["is_negative"].map({"True": True, "False": False, True: True, False: False})
    df["is_multi_seller"] = df["is_multi_seller"].map({"True": True, "False": False, True: True, False: False})
    df["is_interstate"]   = df["is_interstate"].map({"True": True, "False": False, True: True, False: False})
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    return df

@st.cache_data(show_spinner=False)
def load_items():
    return pd.read_csv(os.path.join(DATA, "order_items.csv"), low_memory=False)


def section_header(num, title, owner, color):
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:12px;margin:40px 0 12px;">
            <div style="background:{color};color:white;font-size:11px;font-weight:800;
                        padding:4px 10px;border-radius:20px;white-space:nowrap;">§{num}</div>
            <div style="font-size:18px;font-weight:800;color:#111827;">{title}</div>
            <div style="margin-left:auto;background:#f3f4f6;color:#6b7280;font-size:11px;
                        font-weight:650;padding:3px 10px;border-radius:20px;">{owner}</div>
        </div>""",
        unsafe_allow_html=True,
    )

def insight_box(text, color="#f0f9ff", border="#0ea5e9"):
    st.markdown(
        f"""<div style="background:{color};border-left:4px solid {border};
                        border-radius:0 8px 8px 0;padding:12px 16px;margin:10px 0 18px;
                        font-size:13px;line-height:1.6;color:#1e293b;">{text}</div>""",
        unsafe_allow_html=True,
    )

def divider():
    st.markdown(
        "<hr style='border:none;border-top:1px solid #e5e7eb;margin:40px 0 0;'>",
        unsafe_allow_html=True,
    )


def render_eda_tab():
    if not os.path.isdir(DATA):
        st.error("Run `python preprocess.py` first to generate processed_data/.")
        return

    master = load_master()
    items  = load_items()

    delivered  = master[master["order_status"] == "delivered"].copy()
    reviewed   = master[master["is_negative"].notna()].copy()
    d_reviewed = delivered[delivered["is_negative"].notna()].copy()

    baseline       = d_reviewed["is_negative"].mean() * 100
    on_time_neg    = d_reviewed[~d_reviewed["is_late"]]["is_negative"].mean() * 100
    late_neg       = d_reviewed[d_reviewed["is_late"]]["is_negative"].mean()  * 100
    late_share     = d_reviewed["is_late"].mean() * 100
    late_rev_share = (
        d_reviewed[d_reviewed["is_late"]]["is_negative"].sum() /
        d_reviewed["is_negative"].sum() * 100
    )

    # ── Banner ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    .eda-banner {{
        background:linear-gradient(135deg,#0f172a 0%,#1e293b 60%,#0f3460 100%);
        border-radius:14px;padding:28px 32px 24px;margin-bottom:8px;color:white;
    }}
    .eda-banner h2 {{margin:0 0 6px;font-size:22px;font-weight:800;}}
    .eda-banner p  {{margin:0;font-size:13px;color:#94a3b8;line-height:1.6;}}
    .kpi-row {{display:flex;gap:16px;margin-top:20px;flex-wrap:wrap;}}
    .kpi {{background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);
           border-radius:10px;padding:16px 20px;min-width:140px;}}
    .kpi-val {{font-size:26px;font-weight:900;}}
    .kpi-lbl {{font-size:11px;color:#94a3b8;margin-top:4px;}}
    .kpi-sub {{font-size:10px;color:#64748b;margin-top:2px;}}
    .cliff {{color:#f97316;}} .good {{color:#34d399;}} .warn {{color:#fbbf24;}}
    </style>
    <div class="eda-banner">
        <h2>Exploratory Data Analysis — Week 1 Findings</h2>
        <p>Olist E-Commerce · Sept 2016 – Oct 2018 · {len(master):,} orders · {len(reviewed):,} reviewed</p>
        <div class="kpi-row">
            <div class="kpi">
                <div class="kpi-val cliff">{baseline:.1f}%</div>
                <div class="kpi-lbl">Baseline negative rate</div>
                <div class="kpi-sub">score ≤ 2 of {len(reviewed):,} reviewed orders</div>
            </div>
            <div class="kpi">
                <div class="kpi-val good">{on_time_neg:.1f}%</div>
                <div class="kpi-lbl">On-time negative rate</div>
                <div class="kpi-sub">flat across 60 days of earliness</div>
            </div>
            <div class="kpi">
                <div class="kpi-val cliff">{late_neg:.1f}%</div>
                <div class="kpi-lbl">Late negative rate</div>
                <div class="kpi-sub">{late_neg/on_time_neg:.1f}× jump the moment date passes</div>
            </div>
            <div class="kpi">
                <div class="kpi-val warn">{late_share:.1f}% → {late_rev_share:.0f}%</div>
                <div class="kpi-lbl">Late orders → bad reviews</div>
                <div class="kpi-sub">of deliveries but % of all negatives</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── § 0  Dataset Overview ─────────────────────────────────────────────────
    section_header("0", "Dataset Overview", "All members", "#6366f1")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total orders",     f"{len(master):,}")
    c2.metric("Reviewed orders",  f"{len(reviewed):,}")
    c3.metric("Delivered orders", f"{len(delivered):,}")
    c4.metric("Unique sellers",   f"{master['primary_seller_id'].nunique():,}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique customers", f"{master['customer_unique_id'].nunique():,}")
    dr = master["order_purchase_timestamp"]
    c2.metric("Date range", f"{dr.min().strftime('%b %Y')} – {dr.max().strftime('%b %Y')}")
    c3.metric("Reviewed rate",  f"{len(reviewed)/len(master)*100:.1f}%")
    c4.metric("Delivered rate", f"{len(delivered)/len(master)*100:.1f}%")

    status = master["order_status"].value_counts().reset_index()
    status.columns = ["Status", "Count"]
    status["Share %"] = (status["Count"] / len(master) * 100).round(1)
    st.markdown("**Order status breakdown**")
    st.dataframe(status, use_container_width=True, hide_index=True)

    # ── § 1  Review Score Distribution ───────────────────────────────────────
    divider()
    section_header("1", "Review Score Distribution", "Yash · Finding 01", "#f97316")
    insight_box(
        "Distribution is <strong>bimodal</strong> — 1-star alone (11.5%) outweighs 2-star and 3-star combined. "
        "This is why we report the <strong>negative rate</strong>, not the mean score of 4.09.",
        "#fff7ed", "#f97316"
    )

    dist = reviewed["review_score"].value_counts(normalize=True).sort_index() * 100
    df_dist = pd.DataFrame({
        "Star":    ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
        "Score":   [1, 2, 3, 4, 5],
        "Count":   reviewed["review_score"].value_counts().sort_index().values,
        "Share %": dist.round(2).values,
    })
    st.dataframe(df_dist, use_container_width=True, hide_index=True,
        column_config={"Share %": st.column_config.ProgressColumn("Share %", min_value=0, max_value=100, format="%.1f%%")})
    st.metric("Baseline negative rate (score ≤ 2)", f"{baseline:.2f}%", f"{len(reviewed):,} reviewed orders")

    # ── § 2  The Promise Cliff ────────────────────────────────────────────────
    divider()
    section_header("2", "The Promise Cliff", "Yash · Central Finding", "#ef4444")
    insight_box(
        "Satisfaction holds <strong>almost perfectly flat</strong> across 60 days of earliness, "
        "then falls off a cliff the moment the promised date passes. "
        f"On-time: <strong>{on_time_neg:.1f}%</strong> negative. "
        f"Late: <strong>{late_neg:.1f}%</strong> negative — a <strong>{late_neg/on_time_neg:.1f}× jump</strong>.",
        "#fef2f2", "#ef4444"
    )

    _bins   = [-999, -30, -15, -7, -3, 0, 3, 7, 15, 30, 999]
    _labels = ["30+ early", "15–30 early", "7–15 early", "3–7 early",
               "0–3 early", "0–3 late", "3–7 late", "7–15 late", "15–30 late", "30+ late"]
    d_reviewed["_dbucket"] = pd.cut(d_reviewed["delay_days"], bins=_bins, labels=_labels, right=True)
    cliff = d_reviewed.groupby("_dbucket", observed=True).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"_dbucket": "Delivery vs Promise", "Negative_pct": "Negative %", "Mean_score": "Mean Score"})
    cliff = cliff[cliff["Orders"] >= 200]
    st.dataframe(cliff, use_container_width=True, hide_index=True,
        column_config={
            "Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%"),
            "Mean Score": st.column_config.NumberColumn("Mean Score", format="%.2f"),
        })

    c1, c2, c3 = st.columns(3)
    c1.metric("On-time negative rate",   f"{on_time_neg:.1f}%")
    c2.metric("Late negative rate",      f"{late_neg:.1f}%", f"+{late_neg - on_time_neg:.1f} pts")
    c3.metric("Late share of negatives", f"{late_rev_share:.0f}%", f"from {late_share:.1f}% of orders")

    # ── § 3  Slow vs Broken Promise ───────────────────────────────────────────
    divider()
    section_header("3", "Slow vs Broken Promise", "Yash · Finding 03", "#f97316")
    insight_box(
        "<strong>Being slow annoys (+8 pts across 70 days on-time).</strong> "
        "<strong>Breaking your word enrages (+20 pts in the first 3 days late).</strong> "
        "These have completely different fixes — one is a logistics investment, the other is free: quote later.",
        "#fff7ed", "#f97316"
    )

    on_time = d_reviewed[~d_reviewed["is_late"]].copy()
    on_time["_db"] = pd.cut(on_time["delivery_days"],
        bins=[0, 7, 14, 21, 30, 45, 60, 999],
        labels=["≤7d", "8–14d", "15–21d", "22–30d", "31–45d", "46–60d", "61+d"])
    slow = on_time.groupby("_db", observed=True).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"_db": "Delivery Time (on-time)", "Negative_pct": "Negative %", "Mean_score": "Mean Score"})
    slow = slow[slow["Orders"] >= 200]

    late_only = d_reviewed[d_reviewed["is_late"]].copy()
    late_only["_lb"] = pd.cut(late_only["delay_days"],
        bins=[0, 3, 7, 15, 30, 999],
        labels=["0–3d late", "3–7d late", "7–15d late", "15–30d late", "30+ late"])
    broken = late_only.groupby("_lb", observed=True).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"_lb": "How Late", "Negative_pct": "Negative %", "Mean_score": "Mean Score"})
    broken = broken[broken["Orders"] >= 200]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Among on-time orders — effect of absolute delivery time**")
        st.dataframe(slow, use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})
    with c2:
        st.markdown("**Among late orders — how late matters**")
        st.dataframe(broken, use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})

    # ── § 4  Handling vs Transit ──────────────────────────────────────────────
    divider()
    section_header("4", "Handling Time vs Transit Time", "Yash · Finding 04", "#8b5cf6")
    insight_box(
        f"Median seller handling: <strong>{d_reviewed['handling_days'].median():.1f} days</strong> (approved → carrier). "
        f"Median carrier transit: <strong>{d_reviewed['transit_days'].median():.1f} days</strong> (carrier → customer). "
        "The carrier owns most of the wait — but <strong>handling is what the marketplace can police directly</strong> with an SLA.",
        "#f5f3ff", "#8b5cf6"
    )

    d_reviewed["_hb"] = pd.cut(d_reviewed["handling_days"],
        bins=[0, 1, 2, 3, 5, 7, 14, 999],
        labels=["≤1d", "1–2d", "2–3d", "3–5d", "5–7d", "7–14d", "14+d"])
    h_tbl = d_reviewed.groupby("_hb", observed=True).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"_hb": "Handling Time", "Negative_pct": "Negative %", "Mean_score": "Mean Score"})
    h_tbl = h_tbl[h_tbl["Orders"] >= 200]

    d_reviewed["_tb"] = pd.cut(d_reviewed["transit_days"],
        bins=[0, 5, 7, 10, 14, 21, 31, 999],
        labels=["≤5d", "5–7d", "7–10d", "10–14d", "14–21d", "21–31d", "31+d"])
    t_tbl = d_reviewed.groupby("_tb", observed=True).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"_tb": "Transit Time", "Negative_pct": "Negative %", "Mean_score": "Mean Score"})
    t_tbl = t_tbl[t_tbl["Orders"] >= 200]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Seller handling time**")
        st.dataframe(h_tbl, use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})
    with c2:
        st.markdown("**Carrier transit time**")
        st.dataframe(t_tbl, use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})
    st.caption("2,379 orders in 31+d transit → 71.2% negative. Carrier transit collapses past ~21 days.")

    # ── § 5  Regional Logistics ───────────────────────────────────────────────
    divider()
    section_header("5", "Regional Logistics", "Anushka", "#0ea5e9")
    insight_box(
        "The pattern is monotone: the further a customer is from São Paulo, the longer the wait and the worse the review. "
        "<strong>Rio de Janeiro is the anomaly</strong> — close, reasonably fast (12d median), yet second-worst in the country at 18.3%.",
        "#f0f9ff", "#0ea5e9"
    )

    state_tbl = d_reviewed.groupby("customer_state").agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative",    lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",      lambda x: round(x.mean(), 2)),
        Median_delivery=("delivery_days",lambda x: round(x.median(), 1)),
        Late_pct=("is_late",             lambda x: round(x.mean() * 100, 1)),
        Avg_order=("total_price",        lambda x: round(x.mean(), 1)),
    ).reset_index().rename(columns={
        "customer_state": "State", "Negative_pct": "Negative %",
        "Mean_score": "Mean Score", "Median_delivery": "Median Days",
        "Late_pct": "Late %", "Avg_order": "Avg Order R$",
    }).sort_values("Negative %", ascending=False)
    state_tbl = state_tbl[state_tbl["Orders"] >= 50]
    st.dataframe(state_tbl, use_container_width=True, hide_index=True,
        column_config={
            "Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%"),
            "Late %":     st.column_config.ProgressColumn("Late %",     min_value=0, max_value=100, format="%.1f%%"),
        })

    st.markdown("**Top 20 worst seller → customer state routes (min 30 orders)**")
    route = d_reviewed.groupby(["seller_state", "customer_state"]).agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative",    lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",      lambda x: round(x.mean(), 2)),
        Median_days=("delivery_days",    lambda x: round(x.median(), 1)),
    ).reset_index().rename(columns={
        "seller_state": "Seller State", "customer_state": "Customer State",
        "Negative_pct": "Negative %", "Mean_score": "Mean Score", "Median_days": "Median Days",
    })
    route = route[route["Orders"] >= 30].sort_values("Negative %", ascending=False).head(20)
    st.dataframe(route, use_container_width=True, hide_index=True,
        column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})

    # ── § 6  Seller Performance ───────────────────────────────────────────────
    divider()
    section_header("6", "Seller Performance", "Kannan", "#10b981")

    seller_perf = d_reviewed.groupby("primary_seller_id").agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score",  lambda x: round(x.mean(), 2)),
        Late_pct=("is_late",         lambda x: round(x.mean() * 100, 1)),
        GMV=("total_price", "sum"),
    ).reset_index()

    cutoff    = int(np.ceil(len(seller_perf) * 0.05))
    top5      = seller_perf.nlargest(cutoff, "Orders")
    all_orders = seller_perf["Orders"].sum()
    all_gmv    = seller_perf["GMV"].sum()
    all_neg    = (seller_perf["Orders"] * seller_perf["Negative_pct"] / 100).sum()
    t5_orders  = top5["Orders"].sum()
    t5_gmv     = top5["GMV"].sum()
    t5_neg     = (top5["Orders"] * top5["Negative_pct"] / 100).sum()

    insight_box(
        f"<strong>{cutoff} sellers (top 5%)</strong> carry "
        f"<strong>{t5_orders/all_orders*100:.0f}%</strong> of orders, "
        f"<strong>{t5_gmv/all_gmv*100:.0f}%</strong> of GMV, and "
        f"<strong>{t5_neg/all_neg*100:.0f}%</strong> of all negative reviews. "
        "Negative reviews concentrate <em>at least as tightly</em> as orders — intervention is feasible.",
        "#f0fdf4", "#10b981"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total sellers",   f"{len(seller_perf):,}")
    c2.metric("Top 5% sellers",  f"{cutoff}")
    c3.metric("Their GMV share", f"{t5_gmv/all_gmv*100:.0f}%")
    c4.metric("Their neg share", f"{t5_neg/all_neg*100:.0f}%")

    qual       = seller_perf[seller_perf["Orders"] >= 20]
    worst10pct = int(np.ceil(len(qual) * 0.10))
    worst      = qual.nsmallest(worst10pct, "Mean_score")
    bad_share  = (worst["Orders"] * worst["Negative_pct"] / 100).sum() / all_neg * 100
    gmv_share  = worst["GMV"].sum() / all_gmv * 100
    st.markdown(
        f"**Worst 10% of sellers with ≥20 orders ({worst10pct} sellers):** "
        f"{bad_share:.1f}% of bad orders · {gmv_share:.1f}% of GMV · "
        f"ratio {bad_share/gmv_share:.1f}× → strong intervention candidate"
    )

    st.markdown("**Worst 20 sellers (min 20 orders)**")
    worst20 = qual.nsmallest(20, "Mean_score")[
        ["primary_seller_id", "Orders", "Negative_pct", "Mean_score", "Late_pct", "GMV"]
    ].copy()
    worst20["GMV"] = worst20["GMV"].round(0)
    st.dataframe(worst20, use_container_width=True, hide_index=True,
        column_config={"Negative_pct": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})

    st.markdown("**Seller size vs negative rate**")
    seller_perf["Size"] = pd.cut(seller_perf["Orders"],
        bins=[0, 10, 20, 50, 100, 200, 9999],
        labels=["1–10", "11–20", "21–50", "51–100", "101–200", "201+"])
    size_tbl = seller_perf.groupby("Size", observed=True).agg(
        Sellers=("Orders", "count"),
        Total_orders=("Orders", "sum"),
        Avg_negative_pct=("Negative_pct", lambda x: round(x.mean(), 1)),
    ).reset_index().rename(columns={"Avg_negative_pct": "Avg Negative %", "Total_orders": "Total Orders"})
    st.dataframe(size_tbl, use_container_width=True, hide_index=True)
    st.caption("Spread ~2 pts and runs the wrong way. Seller size is not a risk marker.")

    # ── § 7  Seller Behaviour Drivers ────────────────────────────────────────
    divider()
    section_header("7", "Seller Behaviour Drivers", "Sahib", "#f59e0b")
    insight_box(
        "Driver spread summary — lateness dominates everything else by a factor of 15×. "
        "Freight cost, payment type, and installments are <strong>practically flat</strong> vs the 14.6% baseline.",
        "#fffbeb", "#f59e0b"
    )

    drivers = {
        "Lateness (on-time vs late)":   f"{on_time_neg:.1f}% → {late_neg:.1f}%  =  {late_neg - on_time_neg:.1f} pts",
        "Delay days (0–3 late → 30+)":  "32.1% → 82.4%  =  50 pts",
        "Transit time (≤5d → 31+d)":    "8.8% → 71.2%  =  62 pts",
        "Handling time (≤1d → 14+d)":   "9.9% → 41.5%  =  32 pts",
        "Item price (decile 1 → 10)":   "13.0% → 16.3%  =  3.7 pts",
        "Payment type":                  "~3.7 pts — card, boleto, debit, voucher indistinguishable",
        "Installment count":             "~3.7 pts — mild rise, confounded with price",
        "Freight as share of goods":     "~1.3 pts — customers don't punish high freight cost",
    }
    st.dataframe(
        pd.DataFrame({"Driver": list(drivers.keys()), "Spread": list(drivers.values())}),
        use_container_width=True, hide_index=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Order volume → negative rate**")
        sp2 = d_reviewed.groupby("primary_seller_id").agg(
            Orders=("order_id", "count"),
            Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
            Late_pct=("is_late",         lambda x: round(x.mean() * 100, 1)),
        ).reset_index()
        sp2["Vol"] = pd.cut(sp2["Orders"],
            bins=[0, 1, 5, 20, 50, 200, 9999],
            labels=["1", "2–5", "6–20", "21–50", "51–200", "201+"])
        vol = sp2.groupby("Vol", observed=True).agg(
            Sellers=("Orders", "count"),
            Total_orders=("Orders", "sum"),
            Avg_neg=("Negative_pct",  lambda x: round(x.mean(), 1)),
            Avg_late=("Late_pct",     lambda x: round(x.mean(), 1)),
        ).reset_index().rename(columns={"Vol": "Order Volume", "Avg_neg": "Avg Negative %", "Avg_late": "Avg Late %"})
        st.dataframe(vol, use_container_width=True, hide_index=True)

    with c2:
        st.markdown("**Freight ratio → negative rate**")
        fr_tbl = d_reviewed.groupby(
            pd.cut(d_reviewed["freight_ratio"],
                   bins=[0, 0.1, 0.2, 0.3, 0.5, 1.0, 999],
                   labels=["<10%", "10–20%", "20–30%", "30–50%", "50–100%", ">100%"])
        ).agg(
            Orders=("order_id", "count"),
            Neg_pct=("is_negative",  lambda x: round(x.mean() * 100, 1)),
            Mean_score=("review_score", lambda x: round(x.mean(), 2)),
        ).reset_index().rename(columns={"freight_ratio": "Freight / Price", "Neg_pct": "Negative %", "Mean_score": "Mean Score"})
        fr_tbl = fr_tbl[fr_tbl["Orders"] >= 100]
        st.dataframe(fr_tbl, use_container_width=True, hide_index=True)
        st.caption("1.3 pt spread. Customers don't punish freight cost — only late shipping.")

    # ── § 8  Product & Pricing ────────────────────────────────────────────────
    divider()
    section_header("8", "Product & Pricing", "Ashwanth", "#ec4899")

    item_review = items.merge(
        d_reviewed[["order_id", "is_negative", "review_score"]], on="order_id", how="inner"
    )
    cat_tbl = item_review.groupby("product_category_name_english").agg(
        Orders=("order_id", "nunique"),
        GMV=("price", "sum"),
        Avg_score=("review_score", lambda x: round(x.mean(), 2)),
        Neg_pct=("is_negative",   lambda x: round(x.mean() * 100, 1)),
    ).reset_index().rename(columns={
        "product_category_name_english": "Category",
        "Avg_score": "Mean Score", "Neg_pct": "Negative %",
    })
    cat_tbl["GMV"] = cat_tbl["GMV"].round(0)
    cat_tbl = cat_tbl[cat_tbl["Orders"] >= 50]

    tab1, tab2, tab3 = st.tabs(["Top GMV", "Worst satisfaction", "Invest-vs-Intervene quadrant"])
    with tab1:
        st.dataframe(cat_tbl.sort_values("GMV", ascending=False).head(20),
            use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})
    with tab2:
        st.dataframe(cat_tbl.sort_values("Mean Score").head(15),
            use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})
    with tab3:
        expensive = cat_tbl[
            (cat_tbl["Negative %"] > baseline) &
            (cat_tbl["GMV"] > cat_tbl["GMV"].quantile(0.75))
        ].sort_values("GMV", ascending=False)
        insight_box(
            f"<strong>{len(expensive)} categories</strong> sit in the expensive quadrant: "
            "high revenue AND above-baseline dissatisfaction. Priority intervention targets.",
            "#fdf2f8", "#ec4899"
        )
        st.dataframe(expensive, use_container_width=True, hide_index=True,
            column_config={"Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=100, format="%.1f%%")})

    st.markdown("**Correlations with review score (non-delivery drivers)**")
    corr_cols = ["review_score", "total_price", "total_freight", "freight_ratio",
                 "max_installments", "delivery_days", "delay_days",
                 "handling_days", "transit_days", "n_items", "geo_distance"]
    corr_cols = [c for c in corr_cols if c in d_reviewed.columns]
    corr = d_reviewed[corr_cols].corr(numeric_only=True)["review_score"].drop("review_score").sort_values()
    corr_df = corr.round(3).reset_index()
    corr_df.columns = ["Driver", "Correlation with review_score"]
    st.dataframe(corr_df, use_container_width=True, hide_index=True)

    st.markdown("**Payment type & installments**")
    pay_tbl = d_reviewed.groupby("dominant_payment_type").agg(
        Orders=("order_id", "count"),
        Neg_pct=("is_negative",  lambda x: round(x.mean() * 100, 1)),
        Mean_score=("review_score", lambda x: round(x.mean(), 2)),
    ).reset_index().rename(columns={"dominant_payment_type": "Payment Type", "Neg_pct": "Negative %", "Mean_score": "Mean Score"})
    st.dataframe(pay_tbl.sort_values("Orders", ascending=False), use_container_width=True, hide_index=True)

    # ── § 9  Multi-Seller Orders ──────────────────────────────────────────────
    divider()
    section_header("9", "Multi-Seller Orders — Unresolved Flag", "Yash · Week-2 carry-over", "#64748b")
    insight_box(
        "Multi-seller orders have a <strong>47.2% negative rate</strong> — 3.5× the single-seller rate — "
        "yet show <strong>less lateness</strong> (late rate 1.0% vs 6.7%). "
        "Likely cause: delivery timestamp records only one shipment, so the order can look on-time while "
        "the customer still waits for the rest. "
        "<strong>Do not use lateness figures for multi-seller orders until confirmed.</strong>",
        "#f8fafc", "#64748b"
    )

    multi  = d_reviewed[d_reviewed["is_multi_seller"] == True]
    single = d_reviewed[d_reviewed["is_multi_seller"] == False]
    df_ms = pd.DataFrame({
        "Metric": ["Orders", "Negative rate", "Late rate", "Median delay (days)"],
        "Single-seller": [
            f"{len(single):,}",
            f"{single['is_negative'].mean()*100:.1f}%",
            f"{single['is_late'].mean()*100:.1f}%",
            f"{single['delay_days'].median():.1f}",
        ],
        "Multi-seller": [
            f"{len(multi):,}",
            f"{multi['is_negative'].mean()*100:.1f}%",
            f"{multi['is_late'].mean()*100:.1f}%",
            f"{multi['delay_days'].median():.1f}",
        ],
    })
    st.dataframe(df_ms, use_container_width=True, hide_index=True)

    # ── § 10  Data Quality Flags ──────────────────────────────────────────────
    divider()
    section_header("10", "Data Quality Flags", "Yash · Handed to cleaning owners", "#64748b")

    orders_df = pd.read_csv(os.path.join(DATA, "orders.csv"), low_memory=False)
    n_appr  = int(orders_df["flag_approved_after_carrier"].sum())
    n_deliv = int(orders_df["flag_delivered_before_carrier"].sum())
    n_100d  = int((d_reviewed["delivery_days"] > 100).sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Approval after carrier pickup",   str(n_appr),  "impossible — kept, flagged")
    c2.metric("Delivered before carrier pickup",  str(n_deliv), "impossible — kept, flagged")
    c3.metric("Deliveries > 100 days",            str(n_100d),  "real but extreme — clip on charts")

    st.markdown("""
| Issue | Count | Handling |
|-------|-------|---------|
| Approval timestamp > carrier pickup | 1,359 | Kept with `flag_approved_after_carrier = True`; excluded from timing analyses |
| Customer delivery < carrier pickup | 23 | Kept with `flag_delivered_before_carrier = True`; excluded from timing analyses |
| Delivery > 100 days (max 210d) | 64 | Real orders; charts clipped and labelled |
| Unknown product category | 610 products | Mapped to `"unknown"` — 19.4% negative, 4.8 pts above baseline |
| Orders with no review | 768 | Excluded from rate calculations; not counted as satisfied |
""")

    # ── § 11  Seasonal Pattern ────────────────────────────────────────────────
    divider()
    section_header("11", "Seasonal Pattern", "All members — Fig 09 context", "#0ea5e9")
    insight_box(
        "Monthly late rate and negative rate move together at <strong>r = 0.80</strong>. "
        "Every demand peak (Nov 2017, Feb–Mar 2018) was paid for in reviews. "
        "From April 2018 capacity finally caught up.",
        "#f0f9ff", "#0ea5e9"
    )

    d_reviewed["month"] = d_reviewed["order_purchase_timestamp"].dt.to_period("M").astype(str)
    monthly = d_reviewed.groupby("month").agg(
        Orders=("order_id", "count"),
        Negative_pct=("is_negative", lambda x: round(x.mean() * 100, 1)),
        Late_pct=("is_late",         lambda x: round(x.mean() * 100, 1)),
    ).reset_index().rename(columns={"month": "Month", "Negative_pct": "Negative %", "Late_pct": "Late %"})
    monthly = monthly[monthly["Orders"] >= 200]
    st.dataframe(monthly, use_container_width=True, hide_index=True,
        column_config={
            "Negative %": st.column_config.ProgressColumn("Negative %", min_value=0, max_value=30, format="%.1f%%"),
            "Late %":     st.column_config.ProgressColumn("Late %",     min_value=0, max_value=30, format="%.1f%%"),
        })

    corr_val = monthly[["Negative %", "Late %"]].corr().loc["Negative %", "Late %"]
    st.metric("Monthly correlation: negative rate ↔ late rate", f"r = {corr_val:.2f}")
