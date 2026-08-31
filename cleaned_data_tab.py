import os
import glob

import pandas as pd
import streamlit as st

PROCESSED_DIR = "processed_data"

FILE_META = {
    "master_orders.csv": {
        "label": "Master Orders",
        "description": "One row per order — everything joined. Primary table for all analysis.",
        "icon": "⭐",
    },
    "orders.csv": {
        "label": "Orders",
        "description": "Order lifecycle with parsed dates and derived delivery/delay metrics.",
        "icon": "📦",
    },
    "order_reviews.csv": {
        "label": "Reviews",
        "description": "One review per order (de-duplicated). Includes is_negative flag.",
        "icon": "⭐",
    },
    "order_items_agg.csv": {
        "label": "Order Items (aggregated)",
        "description": "Order-grain: n_items, n_sellers, total_price, freight_ratio, is_multi_seller.",
        "icon": "🛒",
    },
    "order_items.csv": {
        "label": "Order Items (raw)",
        "description": "Item-level rows with category joined. Use for product/category breakdowns.",
        "icon": "🛒",
    },
    "order_payments_agg.csv": {
        "label": "Payments (aggregated)",
        "description": "Order-grain: dominant payment type, max installments, total payment value.",
        "icon": "💳",
    },
    "order_payments.csv": {
        "label": "Payments (raw)",
        "description": "Payment-level rows. Use for payment-type breakdowns.",
        "icon": "💳",
    },
    "products.csv": {
        "label": "Products",
        "description": "English category joined, typos fixed, volume derived, nulls filled.",
        "icon": "📦",
    },
    "customers.csv": {
        "label": "Customers",
        "description": "Normalised city/state, median lat/lng joined from geolocation.",
        "icon": "👤",
    },
    "sellers.csv": {
        "label": "Sellers",
        "description": "Normalised city/state, median lat/lng joined from geolocation.",
        "icon": "🏪",
    },
    "geolocation_zip.csv": {
        "label": "Geolocation",
        "description": "1 M raw rows collapsed to 19 K unique zip codes with median lat/lng.",
        "icon": "📍",
    },
    "closed_deals.csv": {
        "label": "Closed Deals",
        "description": "Seller acquisition data. won_date parsed to datetime.",
        "icon": "🤝",
    },
    "mql.csv": {
        "label": "Marketing Leads (MQL)",
        "description": "Marketing qualified leads. first_contact_date parsed, origin nulls filled.",
        "icon": "📣",
    },
}

BADGE_COLS = {
    "master_orders.csv": ["order_id", "customer_id", "primary_seller_id"],
    "orders.csv": ["order_id", "customer_id"],
    "order_reviews.csv": ["review_id", "order_id"],
    "order_items.csv": ["order_id", "product_id", "seller_id"],
    "order_items_agg.csv": ["order_id", "primary_seller_id"],
    "order_payments.csv": ["order_id"],
    "order_payments_agg.csv": ["order_id"],
    "products.csv": ["product_id"],
    "customers.csv": ["customer_id", "customer_unique_id"],
    "sellers.csv": ["seller_id"],
    "geolocation_zip.csv": ["zip_code_prefix"],
    "closed_deals.csv": ["mql_id", "seller_id"],
    "mql.csv": ["mql_id"],
}

DERIVED_COLS = {
    "orders.csv": ["delay_days", "delivery_days", "handling_days", "transit_days",
                   "promise_buffer_days", "is_late",
                   "flag_approved_after_carrier", "flag_delivered_before_carrier"],
    "order_reviews.csv": ["is_negative"],
    "order_items_agg.csv": ["n_items", "n_sellers", "total_price", "total_freight",
                            "freight_ratio", "is_multi_seller", "all_seller_ids",
                            "n_distinct_categories"],
    "order_payments_agg.csv": ["n_payment_methods", "dominant_payment_type",
                                "max_installments", "total_payment_value"],
    "products.csv": ["product_category_name_english", "product_volume_cm3",
                     "product_name_length", "product_description_length"],
    "customers.csv": ["customer_lat", "customer_lng"],
    "sellers.csv": ["seller_lat", "seller_lng"],
    "geolocation_zip.csv": ["lat", "lng"],
    "master_orders.csv": ["delay_days", "delivery_days", "handling_days", "transit_days",
                          "promise_buffer_days", "is_late", "is_negative",
                          "total_price", "total_freight", "freight_ratio",
                          "n_items", "n_sellers", "is_multi_seller",
                          "dominant_payment_type", "max_installments", "total_payment_value",
                          "primary_category", "delay_bucket", "geo_distance", "is_interstate"],
}


@st.cache_data(show_spinner=False)
def load_processed(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path, low_memory=False, nrows=200)


@st.cache_data(show_spinner=False)
def load_meta(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        return None, None, None
    df = pd.read_csv(path, low_memory=False)
    n_rows = len(df)
    n_cols = len(df.columns)
    null_pct = (df.isna().sum() / len(df) * 100).round(1)
    return n_rows, n_cols, null_pct


def _col_tag(col, filename):
    key_cols = BADGE_COLS.get(filename, [])
    derived   = DERIVED_COLS.get(filename, [])
    if col in key_cols:
        return "key"
    if col in derived:
        return "derived"
    return ""


def render_cleaned_data_tab():
    if not os.path.isdir(PROCESSED_DIR):
        st.error(
            "Processed data not found. Run `python preprocess.py` from the project root first."
        )
        return

    files = [f for f in FILE_META if os.path.exists(os.path.join(PROCESSED_DIR, f))]
    if not files:
        st.error("No processed CSV files found in `processed_data/`.")
        return

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        .clean-banner {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
            border-radius: 14px;
            padding: 28px 32px 24px;
            margin-bottom: 28px;
            color: white;
        }
        .clean-banner h2 { margin: 0 0 6px; font-size: 22px; font-weight: 800; }
        .clean-banner p  { margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.6; }
        .stat-row { display: flex; gap: 24px; margin-top: 20px; flex-wrap: wrap; }
        .stat-box {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 14px 20px;
            min-width: 130px;
        }
        .stat-val { font-size: 22px; font-weight: 800; color: #f97316; }
        .stat-lbl { font-size: 11px; color: #94a3b8; margin-top: 2px; }

        .file-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 0;
            margin-bottom: 16px;
            overflow: hidden;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .file-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: #f8fafc;
            border-bottom: 1px solid #e5e7eb;
        }
        .file-icon { font-size: 20px; }
        .file-title { font-size: 15px; font-weight: 700; color: #111827; }
        .file-desc  { font-size: 12px; color: #6b7280; margin-top: 2px; }
        .file-stats { margin-left: auto; display: flex; gap: 16px; align-items: center; }
        .stat-chip {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 600;
            color: #374151;
            white-space: nowrap;
        }
        .badge-key {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            font-size: 9px;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 4px;
            margin-right: 4px;
            vertical-align: middle;
        }
        .badge-derived {
            display: inline-block;
            background: #d1fae5;
            color: #065f46;
            font-size: 9px;
            font-weight: 800;
            padding: 2px 5px;
            border-radius: 4px;
            margin-right: 4px;
            vertical-align: middle;
        }
        .col-legend {
            display: flex;
            gap: 16px;
            padding: 10px 20px;
            font-size: 11px;
            color: #6b7280;
            border-bottom: 1px solid #f3f4f6;
            background: #fafafa;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    total_rows = 0
    total_cols_set = set()
    for fname in files:
        path = os.path.join(PROCESSED_DIR, fname)
        df_tmp = pd.read_csv(path, nrows=0)
        total_cols_set.update(df_tmp.columns.tolist())
        n, _, _ = load_meta(fname)
        if n:
            total_rows += n

    st.markdown(
        f"""
        <div class="clean-banner">
            <h2>Cleaned Dataset</h2>
            <p>
                Preprocessed by <code>preprocess.py</code> from the raw Olist CSVs.<br>
                Dates parsed · categories translated · duplicates removed · derived columns added · all tables joinable via <code>order_id</code>.
            </p>
            <div class="stat-row">
                <div class="stat-box">
                    <div class="stat-val">{len(files)}</div>
                    <div class="stat-lbl">Clean tables</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{total_rows:,}</div>
                    <div class="stat-lbl">Total rows (all tables)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">{len(total_cols_set)}</div>
                    <div class="stat-lbl">Unique columns</div>
                </div>
                <div class="stat-box">
                    <div class="stat-val">master_orders.csv</div>
                    <div class="stat-lbl">Start analysis here</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Cleaning changes summary ──────────────────────────────────────────────
    with st.expander("What was cleaned and why", expanded=False):
        st.markdown("""
| Change | Detail |
|--------|--------|
| **Date parsing** | All date/timestamp columns converted from strings to `datetime64` |
| **Delivery metrics derived** | `delay_days` (negative = early), `delivery_days`, `handling_days`, `transit_days`, `promise_buffer_days`, `is_late` |
| **Estimated date normalised** | Floored to midnight so "arrived at 14:00 on promised day" = 0 days late, not 0.58 |
| **Impossible timestamps flagged** | 680 orders where approval > carrier pickup — kept with `flag_` columns, not dropped |
| **Reviews de-duplicated** | 99,224 rows → 98,673 unique orders (kept highest score per order) |
| **`is_negative` flag** | `review_score ≤ 2` → `True` |
| **Category translation** | Portuguese `product_category_name` joined with English translation; missing → `"unknown"` |
| **Typo columns renamed** | `product_name_lenght` → `product_name_length`, `product_description_lenght` → `product_description_length` |
| **Product volume derived** | `length × height × width` → `product_volume_cm3` |
| **Numeric nulls filled** | Products: ~1.9% missing → filled with column median |
| **City names normalised** | Title-case, stripped whitespace (sellers + customers) |
| **Geolocation deduped** | 1,000,163 rows → 19,015 unique zip codes with median lat/lng |
| **Lat/lng joined** | Added to both `customers.csv` and `sellers.csv` |
| **Items aggregated to order grain** | `order_items_agg.csv`: n_items, n_sellers, total_price, freight_ratio, is_multi_seller |
| **Payments aggregated to order grain** | `order_payments_agg.csv`: dominant_payment_type, max_installments, total_payment_value |
| **Master table built** | `master_orders.csv` — 45 columns, one row per order, all tables joined |
| **Geo distance** | Euclidean degree-distance seller → customer added to master |
| **Interstate flag** | `is_interstate = customer_state ≠ seller_state` |
""")

    st.markdown("---")

    # ── Per-file cards ────────────────────────────────────────────────────────
    for fname in files:
        meta = FILE_META.get(fname, {"label": fname, "description": "", "icon": "📄"})
        n_rows, n_cols, null_pct = load_meta(fname)
        if n_rows is None:
            continue

        with st.expander(
            f"{meta['icon']}  **{meta['label']}** — {n_rows:,} rows · {n_cols} columns",
            expanded=(fname == "master_orders.csv"),
        ):
            st.markdown(f"*{meta['description']}*")
            st.markdown(
                '<div class="col-legend">'
                '<span><span class="badge-key">KEY</span> ID / join column</span>'
                '<span><span class="badge-derived">NEW</span> Derived / cleaned column (not in raw data)</span>'
                '</div>',
                unsafe_allow_html=True,
            )

            # Column schema
            df_preview = load_processed(fname)
            if df_preview is None:
                continue

            schema_rows = []
            key_cols     = BADGE_COLS.get(fname, [])
            derived_cols = DERIVED_COLS.get(fname, [])

            for col in df_preview.columns:
                tag = ""
                if col in key_cols:
                    tag = "KEY"
                elif col in derived_cols:
                    tag = "NEW"
                null_pct_val = null_pct.get(col, 0.0)
                schema_rows.append({
                    "Column": col,
                    "Type": str(df_preview[col].dtype),
                    "Tag": tag,
                    "Null %": f"{null_pct_val:.1f}%",
                })

            schema_df = pd.DataFrame(schema_rows)

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("**Schema**")
                st.dataframe(
                    schema_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Tag": st.column_config.TextColumn(width="small"),
                        "Null %": st.column_config.TextColumn(width="small"),
                        "Type": st.column_config.TextColumn(width="small"),
                    },
                )
            with col2:
                st.markdown("**Sample rows (first 5)**")
                st.dataframe(df_preview.head(5), use_container_width=True)

            # Download full file
            full_path = os.path.join(PROCESSED_DIR, fname)
            with open(full_path, "rb") as f:
                st.download_button(
                    label=f"Download {fname}",
                    data=f,
                    file_name=fname,
                    mime="text/csv",
                    key=f"dl_{fname}",
                )
