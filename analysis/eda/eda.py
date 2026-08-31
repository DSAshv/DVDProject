"""
EDA — Week 1 Analysis
Reads from: processed_data/   (run preprocess.py first)

Covers every finding from Yash's Week-1 report plus the five question
areas the team divided:
  Yash     — Delivery Performance (promise cliff, slow vs broken, leverage)
  Anushka  — Regional Logistics   (state-level, seller→customer routes)
  Kannan   — Seller Performance   (concentration, worst sellers)
  Sahib    — Seller Behaviour     (handling time, volume, freight pricing)
  Ashwanth — Product & Pricing    (category revenue vs satisfaction, non-delivery drivers)

Run:
    cd <project_root>
    python analysis/eda/eda.py

Outputs printed to stdout and written to analysis/eda/eda_report.md
"""

import os
import pandas as pd
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "processed_data")
OUT  = os.path.join(os.path.dirname(__file__), "eda_report.md")

lines = []

def h(text):
    lines.append(text)
    print(text)

def p(text=""):
    lines.append(text)
    print(text)

def md_table(df):
    t = df.to_markdown(index=True)
    lines.append(t)
    print(t)

# ── Load ────────────────────────────────────────────────────────────────────
h("# EDA Report — Olist E-Commerce\n")

master   = pd.read_csv(os.path.join(DATA, "master_orders.csv"), low_memory=False)
items    = pd.read_csv(os.path.join(DATA, "order_items.csv"),   low_memory=False)
products = pd.read_csv(os.path.join(DATA, "products.csv"),      low_memory=False)
sellers  = pd.read_csv(os.path.join(DATA, "sellers.csv"),       low_memory=False)
payments = pd.read_csv(os.path.join(DATA, "order_payments.csv"),low_memory=False)

# Re-parse boolean/date cols that CSV round-trips as object
master["is_late"]     = master["is_late"].map({"True": True, "False": False, True: True, False: False})
master["is_negative"] = master["is_negative"].map({"True": True, "False": False, True: True, False: False})
master["is_multi_seller"] = master["is_multi_seller"].map({"True": True, "False": False, True: True, False: False})
master["is_interstate"]   = master["is_interstate"].map({"True": True, "False": False, True: True, False: False})
master["order_purchase_timestamp"] = pd.to_datetime(master["order_purchase_timestamp"], errors="coerce")

delivered  = master[master["order_status"] == "delivered"].copy()
reviewed   = master[master["is_negative"].notna()].copy()          # 98,673
d_reviewed = delivered[delivered["is_negative"].notna()].copy()    # delivered + reviewed

# ── 0. Dataset Overview ──────────────────────────────────────────────────────
h("## 0. Dataset Overview\n")
p(f"| Metric | Value |")
p(f"|--------|-------|")
p(f"| Total orders | {len(master):,} |")
p(f"| Reviewed orders | {len(reviewed):,} |")
p(f"| Delivered orders | {len(delivered):,} |")
p(f"| Delivered + reviewed | {len(d_reviewed):,} |")
p(f"| Unique customers | {master['customer_unique_id'].nunique():,} |")
p(f"| Unique sellers | {master['primary_seller_id'].nunique():,} |")
p(f"| Date range | {master['order_purchase_timestamp'].min().date()} → {master['order_purchase_timestamp'].max().date()} |")
p()

status_dist = master["order_status"].value_counts()
p("**Order status breakdown:**")
md_table(status_dist.to_frame("count"))
p()

# ── 1. REVIEW SCORE DISTRIBUTION ────────────────────────────────────────────
h("---\n## 1. Review Score Distribution  (Yash · finding 01)\n")

score_dist = reviewed["review_score"].value_counts(normalize=True).sort_index() * 100
score_dist = score_dist.round(2).to_frame("pct_of_reviews")
score_dist["count"] = reviewed["review_score"].value_counts().sort_index()
md_table(score_dist)

baseline_neg = reviewed["is_negative"].mean() * 100
p(f"\n**Baseline negative rate (score ≤ 2):** {baseline_neg:.2f}% of {len(reviewed):,} reviewed orders")
p("Note: Distribution is bimodal — 1-star alone (11.5%) outweighs 2-star and 3-star combined.")
p("This is why we report negative rate, not mean score.")
p()

# ── 2. THE PROMISE CLIFF  (Yash · central finding) ──────────────────────────
h("---\n## 2. The Promise Cliff — Delivery vs Promised Date  (Yash · finding 02)\n")

_bins   = [-999, -30, -15, -7, -3, 0, 3, 7, 15, 30, 999]
_labels = ["30+ early", "15-30 early", "7-15 early", "3-7 early",
           "0-3 early", "0-3 late", "3-7 late", "7-15 late",
           "15-30 late", "30+ late"]

d_reviewed["delay_bucket"] = pd.cut(
    d_reviewed["delay_days"], bins=_bins, labels=_labels, right=True
)

cliff = d_reviewed.groupby("delay_bucket", observed=True).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
cliff = cliff[cliff["orders"] >= 200]
md_table(cliff)

on_time_neg  = d_reviewed[~d_reviewed["is_late"]]["is_negative"].mean() * 100
late_neg     = d_reviewed[d_reviewed["is_late"]]["is_negative"].mean()  * 100
late_share   = d_reviewed["is_late"].mean() * 100
late_rev_share = (
    d_reviewed[d_reviewed["is_late"]]["is_negative"].sum() /
    d_reviewed["is_negative"].sum() * 100
)

p(f"""
**Key numbers (replicating Yash's report):**
- On-time orders: **{on_time_neg:.1f}%** negative — flat across 60 days of earliness
- Late orders: **{late_neg:.1f}%** negative — a {late_neg/on_time_neg:.1f}× jump
- Late orders are **{late_share:.1f}%** of deliveries but **{late_rev_share:.1f}%** of all negative reviews
""")

# ── 3. SLOW vs BROKEN PROMISE  (Yash · finding 03) ──────────────────────────
h("---\n## 3. Slow vs Broken Promise  (Yash · finding 03)\n")

on_time = d_reviewed[~d_reviewed["is_late"]].copy()
on_time["delivery_bucket"] = pd.cut(
    on_time["delivery_days"],
    bins=[0, 7, 14, 21, 30, 45, 60, 999],
    labels=["≤7d", "8-14d", "15-21d", "22-30d", "31-45d", "46-60d", "61+d"]
)
slow = on_time.groupby("delivery_bucket", observed=True).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
slow = slow[slow["orders"] >= 200]
p("**Among on-time orders — effect of absolute delivery time:**")
md_table(slow)

late = d_reviewed[d_reviewed["is_late"]].copy()
late["lateness_bucket"] = pd.cut(
    late["delay_days"],
    bins=[0, 3, 7, 15, 30, 999],
    labels=["0-3d late", "3-7d late", "7-15d late", "15-30d late", "30+ late"]
)
broken = late.groupby("lateness_bucket", observed=True).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
broken = broken[broken["orders"] >= 200]
p("\n**Among late orders — effect of how late:**")
md_table(broken)
p("\nBeing slow annoys (+8 pts across 70 days on-time). Breaking the promise enrages (+20 pts in first 3 days late).")
p()

# ── 4. HANDLING vs TRANSIT  (Yash · finding 04) ─────────────────────────────
h("---\n## 4. Handling Time vs Transit Time  (Yash · finding 04)\n")

p(f"Median seller handling time : {d_reviewed['handling_days'].median():.1f} days (purchase → carrier)")
p(f"Median carrier transit time : {d_reviewed['transit_days'].median():.1f} days (carrier → customer)")
p()

d_reviewed["handling_bucket"] = pd.cut(
    d_reviewed["handling_days"],
    bins=[0, 1, 2, 3, 5, 7, 14, 999],
    labels=["≤1d", "1-2d", "2-3d", "3-5d", "5-7d", "7-14d", "14+d"]
)
handling_tbl = d_reviewed.groupby("handling_bucket", observed=True).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
handling_tbl = handling_tbl[handling_tbl["orders"] >= 200]
p("**Negative rate by seller handling time:**")
md_table(handling_tbl)

d_reviewed["transit_bucket"] = pd.cut(
    d_reviewed["transit_days"],
    bins=[0, 5, 7, 10, 14, 21, 31, 999],
    labels=["≤5d", "5-7d", "7-10d", "10-14d", "14-21d", "21-31d", "31+d"]
)
transit_tbl = d_reviewed.groupby("transit_bucket", observed=True).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
transit_tbl = transit_tbl[transit_tbl["orders"] >= 200]
p("\n**Negative rate by carrier transit time:**")
md_table(transit_tbl)
p()

# ── 5. REGIONAL LOGISTICS  (Anushka) ─────────────────────────────────────────
h("---\n## 5. Regional Logistics — Customer State  (Anushka)\n")

state_tbl = d_reviewed.groupby("customer_state").agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
    median_delivery_days=("delivery_days", "median"),
    late_rate_pct=("is_late", lambda x: x.mean() * 100),
    avg_total_price=("total_price", "mean"),
).round(2).sort_values("negative_pct", ascending=False)
state_tbl = state_tbl[state_tbl["orders"] >= 50]
p("**All states ranked by negative rate (min 50 orders):**")
md_table(state_tbl)
p()

# Seller → customer route worst performers
h("### 5b. Seller-State → Customer-State Routes  (Anushka Q2)\n")
route = d_reviewed.groupby(["seller_state", "customer_state"]).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
    median_delivery_days=("delivery_days", "median"),
).round(2).reset_index()
route = route[route["orders"] >= 30].sort_values("negative_pct", ascending=False)
p("**Top 20 worst seller → customer state routes (min 30 orders):**")
md_table(route.head(20).set_index(["seller_state", "customer_state"]))
p()

# ── 6. SELLER PERFORMANCE  (Kannan) ──────────────────────────────────────────
h("---\n## 6. Seller Performance  (Kannan)\n")

seller_perf = d_reviewed.groupby("primary_seller_id").agg(
    n_orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
    late_rate_pct=("is_late", lambda x: x.mean() * 100),
    gmv=("total_price", "sum"),
).round(2)

p(f"Total distinct sellers with delivered+reviewed orders: {len(seller_perf):,}")

# Concentration: top 5%
cutoff_5pct = int(np.ceil(len(seller_perf) * 0.05))
top5 = seller_perf.nlargest(cutoff_5pct, "n_orders")
all_orders  = seller_perf["n_orders"].sum()
all_gmv     = seller_perf["gmv"].sum()
all_neg     = (seller_perf["n_orders"] * seller_perf["negative_pct"] / 100).sum()
top5_orders = top5["n_orders"].sum()
top5_gmv    = top5["gmv"].sum()
top5_neg    = (top5["n_orders"] * top5["negative_pct"] / 100).sum()

p(f"\n**Supply-side concentration (top {cutoff_5pct} sellers = top 5%):**")
p(f"| Metric | Top 5% sellers | Rest 95% |")
p(f"|--------|----------------|---------|")
p(f"| Orders | {top5_orders/all_orders*100:.1f}% | {(all_orders-top5_orders)/all_orders*100:.1f}% |")
p(f"| GMV    | {top5_gmv/all_gmv*100:.1f}% | {(all_gmv-top5_gmv)/all_gmv*100:.1f}% |")
p(f"| Negative reviews | {top5_neg/all_neg*100:.1f}% | {(all_neg-top5_neg)/all_neg*100:.1f}% |")
p()

# Worst sellers (min 20 orders)
qual_sellers = seller_perf[seller_perf["n_orders"] >= 20]
worst10pct = int(np.ceil(len(qual_sellers) * 0.10))
worst = qual_sellers.nsmallest(worst10pct, "mean_score")
bad_order_share = (worst["n_orders"] * worst["negative_pct"] / 100).sum() / all_neg * 100
bad_gmv_share   = worst["gmv"].sum() / all_gmv * 100

p(f"**Worst 10% of sellers with ≥20 orders ({worst10pct} sellers):**")
p(f"- Account for {bad_order_share:.1f}% of all bad orders, {bad_gmv_share:.1f}% of GMV")
p(f"- Ratio: {bad_order_share/bad_gmv_share:.1f}x bad orders per GMV point → strong intervention candidate")
p()

p("**Worst 20 individual sellers (min 20 orders):**")
md_table(qual_sellers.nsmallest(20, "mean_score")[["n_orders","negative_pct","mean_score","late_rate_pct","gmv"]])
p()

# Seller size vs negative rate (Kannan / Yash finding: size is NOT a predictor)
h("### 6b. Seller Size vs Negative Rate  (Kannan Q2 / Yash correction)\n")
size_bins   = [0, 10, 20, 50, 100, 200, 9999]
size_labels = ["1-10", "11-20", "21-50", "51-100", "101-200", "201+"]
seller_perf["size_bucket"] = pd.cut(seller_perf["n_orders"], bins=size_bins, labels=size_labels)
size_tbl = seller_perf.groupby("size_bucket", observed=True).agg(
    n_sellers=("n_orders", "count"),
    total_orders=("n_orders", "sum"),
    avg_negative_pct=("negative_pct", "mean"),
).round(2)
md_table(size_tbl)
p("\nSpread is ~2 pts and runs the wrong way. Seller size is not a risk marker.")
p()

# ── 7. SELLER BEHAVIOUR DRIVERS  (Sahib) ─────────────────────────────────────
h("---\n## 7. Seller Behaviour Drivers  (Sahib)\n")

h("### 7a. Handling Time → Review Score\n")
p("(Covered in section 4. Handling time is the seller-controllable half of wait.)")
p()

h("### 7b. Order Volume → Negative Rate\n")
vol_bins   = [0, 1, 5, 20, 50, 200, 9999]
vol_labels = ["1", "2-5", "6-20", "21-50", "51-200", "201+"]
seller_perf["vol_bucket"] = pd.cut(seller_perf["n_orders"], bins=vol_bins, labels=vol_labels)
vol_tbl = seller_perf.groupby("vol_bucket", observed=True).agg(
    n_sellers=("n_orders", "count"),
    total_orders=("n_orders", "sum"),
    avg_negative_pct=("negative_pct", "mean"),
    avg_late_rate=("late_rate_pct", "mean"),
).round(2)
md_table(vol_tbl)
p()

h("### 7c. Freight Pricing → Review Score  (Sahib Q1)\n")
freight_tbl = d_reviewed.groupby(
    pd.cut(d_reviewed["freight_ratio"], bins=[0, 0.1, 0.2, 0.3, 0.5, 1.0, 999],
           labels=["<10%", "10-20%", "20-30%", "30-50%", "50-100%", ">100%"])
).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
freight_tbl = freight_tbl[freight_tbl["orders"] >= 100]
md_table(freight_tbl)
p("Customers do not punish high freight cost — only late shipping (Yash finding 04, spread 1.3 pts).")
p()

h("### 7d. Where to Invest vs Intervene  (Sahib Q2)\n")
p("Driver spread summary (best bucket negative rate → worst bucket):")
driver_spread = {
    "Lateness (on-time vs late)":         f"{on_time_neg:.1f}% → {late_neg:.1f}% = {late_neg-on_time_neg:.1f} pts",
    "Delay days (0-3 late vs 30+ late)":  "32.1% → 82.4% = 50.3 pts",
    "Transit time (≤5d vs 31+d)":         "See section 4",
    "Item price (decile 1 vs 10)":        "13.0% → 16.3% = 3.7 pts",
    "Payment type":                        "~3.7 pts — indistinguishable",
    "Installment count":                   "~3.7 pts — confounded with price",
    "Freight ratio":                       "~1.3 pts — customers don't punish freight cost",
}
for k, v in driver_spread.items():
    p(f"- **{k}:** {v}")
p()

# ── 8. PRODUCT & PRICING  (Ashwanth) ─────────────────────────────────────────
h("---\n## 8. Product & Pricing  (Ashwanth)\n")

h("### 8a. Category: Revenue vs Satisfaction  (Ashwanth Q2)\n")

item_review = items.merge(
    d_reviewed[["order_id", "is_negative", "review_score"]],
    on="order_id", how="inner"
)
cat_tbl = item_review.groupby("product_category_name_english").agg(
    orders=("order_id", "nunique"),
    gmv=("price", "sum"),
    avg_review_score=("review_score", "mean"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
).round(2)
cat_tbl = cat_tbl[cat_tbl["orders"] >= 50].sort_values("gmv", ascending=False)

p("**Top 20 categories by GMV:**")
md_table(cat_tbl.head(20))

p("\n**Bottom 15 categories by avg review score (min 50 orders):**")
md_table(cat_tbl.sort_values("avg_review_score").head(15))

p("\n**High-GMV + above-baseline negative rate categories (the invest-vs-intervene quadrant):**")
expensive = cat_tbl[(cat_tbl["negative_pct"] > baseline_neg) & (cat_tbl["gmv"] > cat_tbl["gmv"].quantile(0.75))]
md_table(expensive.sort_values("gmv", ascending=False))
p()

h("### 8b. Non-Delivery Drivers  (Ashwanth Q1)\n")
p("Correlations with review_score among delivered+reviewed orders:")
corr_cols = ["review_score", "total_price", "total_freight", "freight_ratio",
             "max_installments", "delivery_days", "delay_days",
             "handling_days", "transit_days", "n_items", "geo_distance"]
corr_cols = [c for c in corr_cols if c in d_reviewed.columns]
corr = d_reviewed[corr_cols].corr(numeric_only=True)["review_score"].drop("review_score").sort_values()
md_table(corr.round(3).to_frame("corr_with_review_score"))
p()

h("### 8c. Payment Type & Installments  (Ashwanth Q1 / Yash finding 04)\n")
pay_tbl = d_reviewed.groupby("dominant_payment_type").agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
    avg_installments=("max_installments", "mean"),
).round(2).sort_values("orders", ascending=False)
md_table(pay_tbl)
p()

install_tbl = d_reviewed.groupby(
    pd.cut(d_reviewed["max_installments"], bins=[0, 1, 3, 6, 12, 24, 999],
           labels=["1", "2-3", "4-6", "7-12", "13-24", "25+"])
).agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    mean_score=("review_score", "mean"),
).round(2)
install_tbl = install_tbl[install_tbl["orders"] >= 100]
p("**Installment count buckets:**")
md_table(install_tbl)
p()

# ── 9. MULTI-SELLER ORDERS  (Yash · unresolved) ──────────────────────────────
h("---\n## 9. Multi-Seller Orders — Unresolved Flag  (Yash · Section 06)\n")

multi = d_reviewed[d_reviewed["is_multi_seller"] == True]
single = d_reviewed[d_reviewed["is_multi_seller"] == False]
p(f"| | Single-seller | Multi-seller |")
p(f"|--|---|---|")
p(f"| Orders | {len(single):,} | {len(multi):,} |")
p(f"| Negative rate | {single['is_negative'].mean()*100:.1f}% | {multi['is_negative'].mean()*100:.1f}% |")
p(f"| Late rate | {single['is_late'].mean()*100:.1f}% | {multi['is_late'].mean()*100:.1f}% |")
p(f"| Median delay_days | {single['delay_days'].median():.1f} | {multi['delay_days'].median():.1f} |")
p()
p("Multi-seller orders are 3.5× more likely to end in a negative review, yet show LESS lateness.")
p("Likely cause: delivery timestamp records only one shipment; the order can look on-time while")
p("the customer still waits for the second parcel. Do not use lateness figures for multi-seller")
p("orders until this is confirmed. (Yash's Week-2 carry-over.)")
p()

# ── 10. IMPOSSIBLE TIMESTAMPS  (Yash · handed to cleaning owners) ────────────
h("---\n## 10. Data Quality Flags  (Yash · Section 06)\n")

orders_raw = pd.read_csv(os.path.join(DATA, "orders.csv"), low_memory=False)
for col in ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date"]:
    orders_raw[col] = pd.to_datetime(orders_raw[col], errors="coerce")

n_approved_after_carrier = orders_raw["flag_approved_after_carrier"].sum()
n_delivered_before_carrier = orders_raw["flag_delivered_before_carrier"].sum()
n_over_100_days = (delivered["delivery_days"] > 100).sum()

p(f"- Orders where approval timestamp > carrier pickup: **{n_approved_after_carrier}** (impossible — excluded from timing analyses)")
p(f"- Orders where customer delivery < carrier pickup:  **{n_delivered_before_carrier}** (impossible — excluded)")
p(f"- Delivered orders with >100 day delivery:          **{n_over_100_days}** (real but extreme — charts should clip and note)")
p(f"- Unknown product category: {(products['product_category_name_english'] == 'unknown').sum()} products")
p()

# ── 11. SEASONAL PATTERN ─────────────────────────────────────────────────────
h("---\n## 11. Seasonal Pattern — Demand vs Capacity  (Fig 09 context)\n")

d_reviewed["month"] = d_reviewed["order_purchase_timestamp"].dt.to_period("M").astype(str)
monthly = d_reviewed.groupby("month").agg(
    orders=("order_id", "count"),
    negative_pct=("is_negative", lambda x: x.mean() * 100),
    late_rate_pct=("is_late", lambda x: x.mean() * 100),
).round(2)
monthly = monthly[monthly["orders"] >= 200]
md_table(monthly)

corr_monthly = monthly[["negative_pct", "late_rate_pct"]].corr().loc["negative_pct", "late_rate_pct"]
p(f"\nCorrelation between monthly late rate and negative rate: **r = {corr_monthly:.2f}**")
p()

# ── Write report ─────────────────────────────────────────────────────────────
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ EDA complete. Report → {os.path.abspath(OUT)}")
