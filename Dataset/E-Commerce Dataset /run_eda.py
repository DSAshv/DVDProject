"""
Quick framing EDA for the E-commerce Orders / Delivery / Satisfaction project.

USAGE:
    Place this script in the same directory as your CSV files and run:
        python run_eda.py

    It will look for files by matching keywords in their filenames (so it
    works whether they're named 'orders_dataset.csv', 'olist_orders_dataset.csv',
    'orders.csv', etc.). It writes a single markdown report: eda_summary.md

OUTPUT:
    eda_summary.md  -- paste this back into the chat for question generation.
"""

import glob
import os
import pandas as pd

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

OUT_MD = "eda_summary.md"
md_lines = []


def log(text=""):
    print(text)
    md_lines.append(text)


def find_csv(keyword):
    """Find a csv file in cwd whose name contains all tokens in keyword (case-insensitive)."""
    candidates = glob.glob("*.csv")
    tokens = keyword.lower().split("_")
    for c in candidates:
        cl = c.lower()
        if all(t in cl for t in tokens):
            return c
    return None


def load(keyword, parse_dates=None):
    path = find_csv(keyword)
    if path is None:
        log(f"⚠️  Could not find a CSV matching `{keyword}` in this folder.")
        return None
    try:
        df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)
        log(f"Loaded `{path}` → shape {df.shape}")
        return df
    except Exception as e:
        log(f"⚠️  Failed to load `{path}`: {e}")
        return None


# ---------------------------------------------------------------------------
log("# EDA Summary\n")

# ---- Load tables ----------------------------------------------------------
orders = load("orders", parse_dates=[
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date"
])
reviews = load("order_reviews")
items = load("order_items")
payments = load("order_payments")
products = load("products")
cat_translation = load("product_category_name_translation")
sellers = load("sellers")
customers = load("customers")
closed_deals = load("closed_deals")
mql = load("marketing_qualified_leads")

log("\n---\n")

# ---- 1. Shape & data health -------------------------------------------------
log("## 1. Shape & Data Health\n")
if orders is not None:
    log(f"- Orders date range: **{orders['order_purchase_timestamp'].min()}** to "
        f"**{orders['order_purchase_timestamp'].max()}**")
    log(f"- Order status breakdown:\n\n{orders['order_status'].value_counts().to_frame().to_markdown()}\n")
    key_cols = ["order_delivered_customer_date", "order_delivered_carrier_date", "order_approved_at"]
    for c in key_cols:
        if c in orders.columns:
            null_pct = orders[c].isna().mean() * 100
            log(f"- Missing `{c}`: {null_pct:.2f}%")

if products is not None and "product_category_name" in products.columns:
    log(f"- Missing `product_category_name` in products: {products['product_category_name'].isna().mean()*100:.2f}%")

if reviews is not None and "review_comment_message" in reviews.columns:
    log(f"- Missing `review_comment_message`: {reviews['review_comment_message'].isna().mean()*100:.2f}%")

log("\n---\n")

# ---- 2. Review score distribution ------------------------------------------
log("## 2. Review Score Distribution\n")
if reviews is not None and "review_score" in reviews.columns:
    dist = reviews["review_score"].value_counts(normalize=True).sort_index() * 100
    log(dist.round(2).to_frame("pct_of_reviews").to_markdown())
log("\n---\n")

# ---- Build a master order-level frame for delay/review joins --------------
master = None
if orders is not None and reviews is not None:
    master = orders.merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
    delivered = master[master["order_status"] == "delivered"].copy()
    delivered["delay_days"] = (
        delivered["order_delivered_customer_date"] - delivered["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    # ---- 3. Delivery delay distribution ------------------------------------
    log("## 3. Delivery Delay (days late vs. estimate), delivered orders only\n")
    log(delivered["delay_days"].describe().round(2).to_frame().to_markdown())

    bins = [-999, -7, -3, -1, 0, 1, 3, 7, 14, 999]
    labels = ["<-7 (very early)", "-7to-3", "-3to-1", "-1to0", "0to1",
              "1to3", "3to7", "7to14", ">14 (very late)"]
    delivered["delay_bucket"] = pd.cut(delivered["delay_days"], bins=bins, labels=labels)
    bucket_summary = delivered.groupby("delay_bucket", observed=True).agg(
        n_orders=("order_id", "count"),
        avg_review_score=("review_score", "mean")
    ).round(3)
    log("\n**Avg review score by delay bucket:**\n")
    log(bucket_summary.to_markdown())
    log("\n---\n")

# ---- 4. Category-level snapshot --------------------------------------------
log("## 4. Category-Level Snapshot (top 15 by order volume)\n")
if items is not None and products is not None and master is not None:
    item_prod = items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
    if cat_translation is not None:
        item_prod = item_prod.merge(cat_translation, on="product_category_name", how="left")
        cat_col = "product_category_name_english"
    else:
        cat_col = "product_category_name"

    order_cat = item_prod[["order_id", cat_col]].drop_duplicates()
    cat_master = order_cat.merge(master[["order_id", "review_score"]], on="order_id", how="left")
    if delivered is not None:
        cat_master = cat_master.merge(
            delivered[["order_id", "delay_days"]], on="order_id", how="left"
        )

    cat_summary = cat_master.groupby(cat_col).agg(
        n_orders=("order_id", "count"),
        avg_review_score=("review_score", "mean"),
        avg_delay_days=("delay_days", "mean")
    ).round(3).sort_values("n_orders", ascending=False)

    log(cat_summary.head(15).to_markdown())
    log("\n**Bottom 10 categories by avg review score (min 30 orders):**\n")
    filtered = cat_summary[cat_summary["n_orders"] >= 30].sort_values("avg_review_score")
    log(filtered.head(10).to_markdown())
    log("\n---\n")

# ---- 5. Seller-level snapshot ----------------------------------------------
log("## 5. Seller-Level Snapshot\n")
if items is not None and master is not None:
    order_seller = items[["order_id", "seller_id"]].drop_duplicates()
    seller_master = order_seller.merge(master[["order_id", "review_score"]], on="order_id", how="left")
    if delivered is not None:
        seller_master = seller_master.merge(
            delivered[["order_id", "delay_days"]], on="order_id", how="left"
        )
    seller_summary = seller_master.groupby("seller_id").agg(
        n_orders=("order_id", "count"),
        avg_review_score=("review_score", "mean"),
        avg_delay_days=("delay_days", "mean")
    ).round(3)

    log(f"- Total distinct sellers with orders: {seller_summary.shape[0]}")
    top20pct_cutoff = int(len(seller_summary) * 0.2)
    top_sellers_by_volume = seller_summary.sort_values("n_orders", ascending=False)
    vol_share = top_sellers_by_volume.head(top20pct_cutoff)["n_orders"].sum() / seller_summary["n_orders"].sum()
    log(f"- Top 20% of sellers by order count generate **{vol_share*100:.1f}%** of all orders")

    log("\n**Worst 10 sellers by avg review score (min 20 orders):**\n")
    filtered_sellers = seller_summary[seller_summary["n_orders"] >= 20].sort_values("avg_review_score")
    log(filtered_sellers.head(10).to_markdown())
    log("\n---\n")

# ---- 6. State-level snapshot ------------------------------------------------
log("## 6. State-Level Snapshot\n")
if customers is not None and sellers is not None and items is not None and master is not None:
    order_cust_state = orders[["order_id", "customer_id"]].merge(
        customers[["customer_id", "customer_state"]], on="customer_id", how="left"
    )
    state_master = order_cust_state.merge(master[["order_id", "review_score"]], on="order_id", how="left")
    if delivered is not None:
        state_master = state_master.merge(delivered[["order_id", "delay_days"]], on="order_id", how="left")

    state_summary = state_master.groupby("customer_state").agg(
        n_orders=("order_id", "count"),
        avg_review_score=("review_score", "mean"),
        avg_delay_days=("delay_days", "mean")
    ).round(3).sort_values("n_orders", ascending=False)

    log(state_summary.to_markdown())
    log("\n---\n")

# ---- 7. Price / freight / installments vs review ---------------------------
log("## 7. Price, Freight & Installments vs Review Score\n")
if items is not None and payments is not None and master is not None:
    order_price = items.groupby("order_id").agg(
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum")
    ).reset_index()
    order_price["freight_ratio"] = order_price["total_freight"] / order_price["total_price"].replace(0, pd.NA)

    order_pay = payments.groupby("order_id").agg(
        max_installments=("payment_installments", "max"),
        total_payment=("payment_value", "sum")
    ).reset_index()

    price_master = order_price.merge(order_pay, on="order_id", how="left").merge(
        master[["order_id", "review_score"]], on="order_id", how="left"
    )

    corr_cols = ["total_price", "total_freight", "freight_ratio", "max_installments", "review_score"]
    corr_cols = [c for c in corr_cols if c in price_master.columns]
    log("**Correlation matrix:**\n")
    log(price_master[corr_cols].corr(numeric_only=True).round(3).to_markdown())
    log("\n---\n")

# ---- 8. Product listing quality vs review ----------------------------------
log("## 8. Product Listing Quality vs Review Score\n")
if items is not None and products is not None and master is not None:
    item_listing = items.merge(
        products[["product_id", "product_photos_qty", "product_description_lenght", "product_weight_g"]],
        on="product_id", how="left"
    )
    order_listing = item_listing.groupby("order_id").agg(
        avg_photos=("product_photos_qty", "mean"),
        avg_desc_len=("product_description_lenght", "mean"),
        avg_weight_g=("product_weight_g", "mean")
    ).reset_index()
    listing_master = order_listing.merge(master[["order_id", "review_score"]], on="order_id", how="left")
    corr_cols = ["avg_photos", "avg_desc_len", "avg_weight_g", "review_score"]
    log(listing_master[corr_cols].corr(numeric_only=True).round(3).to_markdown())
    log("\n---\n")

# ---- 9. Funnel-to-fulfillment coverage -------------------------------------
log("## 9. Marketing Funnel → Seller Coverage\n")
if closed_deals is not None and sellers is not None:
    matched = closed_deals["seller_id"].isin(sellers["seller_id"]).sum()
    log(f"- `closed_deals_dataset` rows: {len(closed_deals)}")
    log(f"- Of those, sellers that also appear in `sellers_dataset`: {matched} "
        f"({matched/len(closed_deals)*100:.1f}%)")
    if items is not None:
        sellers_with_orders = set(items["seller_id"].unique())
        matched_with_orders = closed_deals["seller_id"].isin(sellers_with_orders).sum()
        log(f"- Of those, sellers with at least one actual order: {matched_with_orders} "
            f"({matched_with_orders/len(closed_deals)*100:.1f}%)")
log("\n---\n")

# ---- Write out --------------------------------------------------------------
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"\n✅ Done. Report written to {os.path.abspath(OUT_MD)}")