"""
Preprocessing pipeline for the Olist E-Commerce dataset.

Run once from the project root:
    python preprocess.py

Reads raw CSVs from  : Dataset/E-Commerce Dataset/
Writes cleaned CSVs to: processed_data/

All downstream analysis (EDA, charts, dashboards) should import from
processed_data/ and never touch the raw files again.

-----------------------------------------------------------------------
What this pipeline does per table
-----------------------------------------------------------------------
orders
  - Parse all five date columns to datetime
  - Normalise order_status to lowercase / stripped
  - Flag and clip impossible timestamps (approved after carrier pickup,
    delivered before carrier pickup) rather than silently dropping them
  - Derive delivery_days, handling_days, transit_days, delay_days,
    promise_buffer_days, is_late, is_negative (boolean helpers)
  - Keep ALL statuses; analysis scripts filter to 'delivered' themselves

order_reviews
  - Parse date columns
  - De-duplicate: keep the review with the highest score per order_id
    (99,224 rows → unique order_id)
  - Add is_negative flag (score <= 2)

order_items
  - Parse shipping_limit_date
  - Aggregate to ORDER grain: n_items, n_sellers, total_price,
    total_freight, freight_ratio, first seller_id, all seller_ids
  - Keep item-level file as well for category/seller lookups

products
  - Join English category name from translation table
  - Fill missing category with "unknown"
  - Rename typo columns: product_name_lenght → product_name_length,
    product_description_lenght → product_description_length

order_payments
  - Keep payment-level file for type breakdowns
  - Aggregate to ORDER grain: dominant payment_type, max installments,
    total payment value, n_payment_methods

sellers / customers / geolocation
  - Normalise city names to title-case, strip whitespace
  - geolocation: deduplicate by zip_code_prefix keeping median lat/lng
  - sellers / customers: join median lat/lng from geolocation

closed_deals / mql
  - Parse date columns
  - Keep as-is; too sparse (842 rows) to impute heavily

master_orders  (the single analysis table)
  - One row per order_id
  - Joins: orders + reviews + items_agg + payments_agg +
           customers + sellers (via items_agg) + products (category)
  - This is the table every team member's scripts should start from
"""

import os
import pandas as pd
import numpy as np

RAW = os.path.join("Dataset", "E-Commerce Dataset ")
OUT = "processed_data"
os.makedirs(OUT, exist_ok=True)

DATE_COLS_ORDERS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

def save(df, name):
    path = os.path.join(OUT, name)
    df.to_csv(path, index=False)
    print(f"  saved {name}  shape={df.shape}")
    return df


# ============================================================
# 1. ORDERS
# ============================================================
print("\n[1/9] orders")
orders = pd.read_csv(os.path.join(RAW, "orders_dataset.csv"), low_memory=False)
orders["order_status"] = orders["order_status"].str.strip().str.lower()

for col in DATE_COLS_ORDERS:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

# estimated_delivery_date is midnight → floor actual delivery to date too
# so "arrived at 14:00 on the promised day" is 0 days late, not 0.58
orders["_actual_date"] = orders["order_delivered_customer_date"].dt.normalize()
orders["_estimated_date"] = orders["order_estimated_delivery_date"].dt.normalize()

orders["delay_days"] = (
    orders["_actual_date"] - orders["_estimated_date"]
).dt.days  # negative = early

orders["delivery_days"] = (
    orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]
).dt.total_seconds() / 86400

orders["handling_days"] = (
    orders["order_delivered_carrier_date"] - orders["order_approved_at"]
).dt.total_seconds() / 86400

orders["transit_days"] = (
    orders["order_delivered_customer_date"] - orders["order_delivered_carrier_date"]
).dt.total_seconds() / 86400

orders["promise_buffer_days"] = (
    orders["_estimated_date"] - orders["order_purchase_timestamp"].dt.normalize()
).dt.days

orders["is_late"] = orders["delay_days"] > 0

# Flag impossible timestamps (clip, not drop — preserve for analysis)
orders["flag_approved_after_carrier"] = (
    orders["order_approved_at"] > orders["order_delivered_carrier_date"]
)
orders["flag_delivered_before_carrier"] = (
    orders["order_delivered_customer_date"] < orders["order_delivered_carrier_date"]
)

orders = orders.drop(columns=["_actual_date", "_estimated_date"])
save(orders, "orders.csv")


# ============================================================
# 2. ORDER REVIEWS
# ============================================================
print("\n[2/9] order_reviews")
reviews = pd.read_csv(os.path.join(RAW, "order_reviews_dataset.csv"), low_memory=False)
reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")
reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"], errors="coerce")

# Some orders have multiple reviews; keep highest score (most conservative —
# customer can improve but not worsen their final sentiment)
reviews = reviews.sort_values("review_score", ascending=False).drop_duplicates(
    subset="order_id", keep="first"
)
reviews["is_negative"] = reviews["review_score"] <= 2
save(reviews, "order_reviews.csv")


# ============================================================
# 3. PRODUCTS  (with English category + typo fixes)
# ============================================================
print("\n[3/9] products")
products = pd.read_csv(os.path.join(RAW, "products_dataset.csv"), low_memory=False)
cat_trans = pd.read_csv(
    os.path.join(RAW, "product_category_name_translation.csv"), low_memory=False
)

products = products.merge(cat_trans, on="product_category_name", how="left")
products["product_category_name_english"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"])
    .fillna("unknown")
    .str.strip()
    .str.replace("_", " ")
    .str.lower()
)

products = products.rename(columns={
    "product_name_lenght": "product_name_length",
    "product_description_lenght": "product_description_length",
})

# Fill remaining numeric nulls with median (only ~1.9% missing)
for col in ["product_name_length", "product_description_length",
            "product_photos_qty", "product_weight_g",
            "product_length_cm", "product_height_cm", "product_width_cm"]:
    if col in products.columns:
        products[col] = products[col].fillna(products[col].median())

products["product_volume_cm3"] = (
    products["product_length_cm"] * products["product_height_cm"] * products["product_width_cm"]
)
save(products, "products.csv")


# ============================================================
# 4. ORDER ITEMS  (item-level + order-grain aggregate)
# ============================================================
print("\n[4/9] order_items")
items = pd.read_csv(os.path.join(RAW, "order_items_dataset.csv"), low_memory=False)
items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"], errors="coerce")

# Join category for item-level lookups
items = items.merge(
    products[["product_id", "product_category_name_english"]],
    on="product_id", how="left"
)
save(items, "order_items.csv")

# Order-grain aggregate
items_agg = items.groupby("order_id").agg(
    n_items=("order_item_id", "max"),           # order_item_id is sequential per order
    n_sellers=("seller_id", "nunique"),
    total_price=("price", "sum"),
    total_freight=("freight_value", "sum"),
    primary_seller_id=("seller_id", "first"),   # seller of item 1
    all_seller_ids=("seller_id", lambda s: "|".join(s.unique())),
    n_distinct_categories=("product_category_name_english", "nunique"),
    primary_category=("product_category_name_english", "first"),
).reset_index()

items_agg["freight_ratio"] = np.where(
    items_agg["total_price"] > 0,
    items_agg["total_freight"] / items_agg["total_price"],
    np.nan,
)
items_agg["is_multi_seller"] = items_agg["n_sellers"] > 1
save(items_agg, "order_items_agg.csv")


# ============================================================
# 5. ORDER PAYMENTS  (payment-level + order-grain aggregate)
# ============================================================
print("\n[5/9] order_payments")
payments = pd.read_csv(os.path.join(RAW, "order_payments_dataset.csv"), low_memory=False)
save(payments, "order_payments.csv")

payments_agg = payments.groupby("order_id").agg(
    n_payment_methods=("payment_type", "nunique"),
    dominant_payment_type=("payment_type", lambda s: s.value_counts().index[0]),
    max_installments=("payment_installments", "max"),
    total_payment_value=("payment_value", "sum"),
).reset_index()
save(payments_agg, "order_payments_agg.csv")


# ============================================================
# 6. GEOLOCATION  (deduplicate by zip → median lat/lng)
# ============================================================
print("\n[6/9] geolocation")
geo = pd.read_csv(os.path.join(RAW, "geolocation_dataset.csv"), low_memory=False)
geo["geolocation_city"] = geo["geolocation_city"].str.strip().str.title()

geo_zip = (
    geo.groupby("geolocation_zip_code_prefix")
    .agg(
        lat=("geolocation_lat", "median"),
        lng=("geolocation_lng", "median"),
        city=("geolocation_city", "first"),
        state=("geolocation_state", "first"),
    )
    .reset_index()
    .rename(columns={"geolocation_zip_code_prefix": "zip_code_prefix"})
)
save(geo_zip, "geolocation_zip.csv")


# ============================================================
# 7. CUSTOMERS
# ============================================================
print("\n[7/9] customers")
customers = pd.read_csv(os.path.join(RAW, "customers_dataset.csv"), low_memory=False)
customers["customer_city"] = customers["customer_city"].str.strip().str.title()
customers["customer_state"] = customers["customer_state"].str.strip().str.upper()

customers = customers.merge(
    geo_zip[["zip_code_prefix", "lat", "lng"]].rename(
        columns={"zip_code_prefix": "customer_zip_code_prefix",
                 "lat": "customer_lat", "lng": "customer_lng"}
    ),
    on="customer_zip_code_prefix", how="left"
)
save(customers, "customers.csv")


# ============================================================
# 8. SELLERS
# ============================================================
print("\n[8/9] sellers")
sellers = pd.read_csv(os.path.join(RAW, "sellers_dataset.csv"), low_memory=False)
sellers["seller_city"] = sellers["seller_city"].str.strip().str.title()
sellers["seller_state"] = sellers["seller_state"].str.strip().str.upper()

sellers = sellers.merge(
    geo_zip[["zip_code_prefix", "lat", "lng"]].rename(
        columns={"zip_code_prefix": "seller_zip_code_prefix",
                 "lat": "seller_lat", "lng": "seller_lng"}
    ),
    on="seller_zip_code_prefix", how="left"
)
save(sellers, "sellers.csv")


# ============================================================
# 9. CLOSED DEALS + MQL
# ============================================================
print("\n[9/9] closed_deals + mql")
closed = pd.read_csv(os.path.join(RAW, "closed_deals_dataset.csv"), low_memory=False)
closed["won_date"] = pd.to_datetime(closed["won_date"], errors="coerce")
save(closed, "closed_deals.csv")

mql = pd.read_csv(os.path.join(RAW, "marketing_qualified_leads_dataset.csv"), low_memory=False)
mql["first_contact_date"] = pd.to_datetime(mql["first_contact_date"], errors="coerce")
mql["origin"] = mql["origin"].fillna("unknown")
save(mql, "mql.csv")


# ============================================================
# MASTER ORDERS TABLE  (one row per order, everything joined)
# ============================================================
print("\n[MASTER] building master_orders.csv")

master = (
    orders
    .merge(reviews[["order_id", "review_score", "is_negative", "review_creation_date"]], on="order_id", how="left")
    .merge(items_agg, on="order_id", how="left")
    .merge(payments_agg, on="order_id", how="left")
    .merge(customers[["customer_id", "customer_unique_id",
                       "customer_state", "customer_city",
                       "customer_lat", "customer_lng"]], on="customer_id", how="left")
    .merge(sellers[["seller_id", "seller_state", "seller_city",
                    "seller_lat", "seller_lng"]].rename(
               columns={"seller_id": "primary_seller_id"}),
           on="primary_seller_id", how="left")
)

# Convenience bucket: delay bucket for delivered orders
_bins   = [-999, -30, -15, -7, -3, 0, 3, 7, 15, 30, 999]
_labels = ["30+ early", "15-30 early", "7-15 early", "3-7 early",
           "0-3 early", "0-3 late", "3-7 late", "7-15 late",
           "15-30 late", "30+ late"]
master["delay_bucket"] = pd.cut(
    master["delay_days"], bins=_bins, labels=_labels, right=True
)

# Distance proxy: Euclidean degree-distance seller → customer
# (not km, but monotone with actual distance for Brazilian lat/lng range)
master["geo_distance"] = np.sqrt(
    (master["customer_lat"] - master["seller_lat"]) ** 2
    + (master["customer_lng"] - master["seller_lng"]) ** 2
)

master["is_interstate"] = master["customer_state"] != master["seller_state"]

save(master, "master_orders.csv")

print("\n✅ Preprocessing complete.")
print(f"   Output folder : {os.path.abspath(OUT)}/")
print(f"   Files written : {len(os.listdir(OUT))}")
print("\nFiles:")
for f in sorted(os.listdir(OUT)):
    path = os.path.join(OUT, f)
    df   = pd.read_csv(path, nrows=0)
    size = os.path.getsize(path) // 1024
    print(f"  {f:<35}  {size:>5} KB")
