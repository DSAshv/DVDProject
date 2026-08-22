# EDA Summary

Loaded `orders_dataset.csv` → shape (99441, 8)
Loaded `order_reviews_dataset.csv` → shape (99224, 7)
Loaded `order_items_dataset.csv` → shape (112650, 7)
Loaded `order_payments_dataset.csv` → shape (103886, 5)
Loaded `products_dataset.csv` → shape (32951, 9)
Loaded `product_category_name_translation.csv` → shape (71, 2)
Loaded `sellers_dataset.csv` → shape (3095, 4)
Loaded `customers_dataset.csv` → shape (99441, 5)
Loaded `closed_deals_dataset.csv` → shape (842, 14)
Loaded `marketing_qualified_leads_dataset.csv` → shape (8000, 4)

---

## 1. Shape & Data Health

- Orders date range: **2016-09-04 21:15:19** to **2018-10-17 17:30:18**
- Order status breakdown:

| order_status   |   count |
|:---------------|--------:|
| delivered      |   96478 |
| shipped        |    1107 |
| canceled       |     625 |
| unavailable    |     609 |
| invoiced       |     314 |
| processing     |     301 |
| created        |       5 |
| approved       |       2 |

- Missing `order_delivered_customer_date`: 2.98%
- Missing `order_delivered_carrier_date`: 1.79%
- Missing `order_approved_at`: 0.16%
- Missing `product_category_name` in products: 1.85%
- Missing `review_comment_message`: 58.70%

---

## 2. Review Score Distribution

|   review_score |   pct_of_reviews |
|---------------:|-----------------:|
|              1 |            11.51 |
|              2 |             3.18 |
|              3 |             8.24 |
|              4 |            19.29 |
|              5 |            57.78 |

---

## 3. Delivery Delay (days late vs. estimate), delivered orders only

|       |   delay_days |
|:------|-------------:|
| count |     96999    |
| mean  |       -11.18 |
| std   |        10.18 |
| min   |      -146.02 |
| 25%   |       -16.24 |
| 50%   |       -11.95 |
| 75%   |        -6.39 |
| max   |       188.98 |

**Avg review score by delay bucket:**

| delay_bucket     |   n_orders |   avg_review_score |
|:-----------------|-----------:|-------------------:|
| <-7 (very early) |      71708 |              4.316 |
| -7to-3           |      12657 |              4.226 |
| -3to-1           |       3300 |              4.122 |
| -1to0            |       1469 |              4.153 |
| 0to1             |       1303 |              4.033 |
| 1to3             |       1374 |              3.511 |
| 3to7             |       1823 |              2.316 |
| 7to14            |       1800 |              1.749 |
| >14 (very late)  |       1565 |              1.71  |

---

## 4. Category-Level Snapshot (top 15 by order volume)

| product_category_name_english   |   n_orders |   avg_review_score |   avg_delay_days |
|:--------------------------------|-----------:|-------------------:|-----------------:|
| bed_bath_table                  |       9772 |              3.965 |          -10.684 |
| health_beauty                   |       8999 |              4.185 |          -11.298 |
| sports_leisure                  |       7876 |              4.171 |          -11.255 |
| computers_accessories           |       6842 |              4.026 |          -11.71  |
| furniture_decor                 |       6622 |              4.001 |          -11.74  |
| housewares                      |       5948 |              4.144 |          -11.441 |
| watches_gifts                   |       5654 |              4.066 |          -11.099 |
| telephony                       |       4212 |              4.006 |          -10.568 |
| auto                            |       3947 |              4.092 |          -10.492 |
| toys                            |       3910 |              4.186 |          -11.315 |
| cool_stuff                      |       3660 |              4.169 |          -11.709 |
| garden_tools                    |       3548 |              4.131 |          -11.144 |
| perfumery                       |       3205 |              4.189 |          -11.643 |
| baby                            |       2909 |              4.042 |          -10.796 |
| electronics                     |       2553 |              4.096 |          -10.308 |

**Bottom 10 categories by avg review score (min 30 orders):**

| product_category_name_english     |   n_orders |   avg_review_score |   avg_delay_days |
|:----------------------------------|-----------:|-------------------:|-----------------:|
| office_furniture                  |       1288 |              3.62  |          -11.105 |
| fashion_male_clothing             |        112 |              3.703 |          -12.725 |
| fashio_female_clothing            |         43 |              3.791 |          -11.419 |
| audio                             |        353 |              3.814 |           -9.338 |
| furniture_mattress_and_upholstery |         38 |              3.816 |           -6.478 |
| construction_tools_safety         |        167 |              3.849 |          -12.218 |
| home_confort                      |        406 |              3.851 |           -9.22  |
| fixed_telephony                   |        220 |              3.903 |          -14.18  |
| fashion_underwear_beach           |        121 |              3.933 |           -9.781 |
| bed_bath_table                    |       9772 |              3.965 |          -10.684 |

---

## 5. Seller-Level Snapshot

- Total distinct sellers with orders: 3095
- Top 20% of sellers by order count generate **83.0%** of all orders

**Worst 10 sellers by avg review score (min 20 orders):**

| seller_id                        |   n_orders |   avg_review_score |   avg_delay_days |
|:---------------------------------|-----------:|-------------------:|-----------------:|
| 4342d4b2ba6b161468c63a7e7cfce593 |         20 |              1.263 |           -5.593 |
| ffff564a4f9085cd26170f4732393726 |         20 |              2.1   |          -47.549 |
| 1ca7077d890b907f89be8c954a02686a |        115 |              2.333 |           -5.962 |
| 2eb70248d66e0e3ef83659f71b244378 |        205 |              2.692 |           -9.2   |
| b19f3ca2ea475913750f25a5c37c8d8f |         24 |              2.792 |           -6.373 |
| 4c8b8048e33af2bf94f2eb547746a916 |         23 |              2.957 |           -4.419 |
| d71d863e5ef30d94e440c11be17dcd8f |         29 |              2.962 |           -9.218 |
| 54965bbe3e4f07ae045b90b0b8541f52 |         78 |              3     |           -2.875 |
| a49928bcdf77c55c6d6e05e09a9b4ca5 |         98 |              3.01  |           -3.678 |
| 972d0f9cf61b499a4812cf0bfa3ad3c4 |         83 |              3.025 |           -9.055 |

---

## 6. State-Level Snapshot

| customer_state   |   n_orders |   avg_review_score |   avg_delay_days |
|:-----------------|-----------:|-------------------:|-----------------:|
| SP               |      42388 |              4.174 |          -10.403 |
| RJ               |      13072 |              3.873 |          -11.029 |
| MG               |      11846 |              4.137 |          -12.587 |
| RS               |       5582 |              4.134 |          -13.209 |
| PR               |       5102 |              4.178 |          -12.586 |
| SC               |       3679 |              4.068 |          -10.75  |
| BA               |       3431 |              3.861 |          -10.071 |
| DF               |       2198 |              4.062 |          -11.266 |
| GO               |       2071 |              4.041 |          -11.53  |
| ES               |       2061 |              4.047 |           -9.808 |
| PE               |       1685 |              4.017 |          -12.79  |
| CE               |       1345 |              3.844 |          -10.15  |
| PA               |        993 |              3.855 |          -13.349 |
| MT               |        916 |              4.106 |          -13.782 |
| MA               |        759 |              3.776 |           -9.099 |
| MS               |        748 |              4.137 |          -10.331 |
| PB               |        539 |              4.023 |          -12.646 |
| PI               |        498 |              3.925 |          -10.601 |
| RN               |        491 |              4.107 |          -12.995 |
| AL               |        425 |              3.732 |           -8.053 |
| SE               |        350 |              3.808 |           -9.329 |
| TO               |        280 |              4.097 |          -11.44  |
| RO               |        253 |              4.052 |          -19.397 |
| AM               |        151 |              4.141 |          -18.818 |
| AC               |         81 |              4.049 |          -20.077 |
| AP               |         68 |              4.194 |          -19.059 |
| RR               |         46 |              3.609 |          -16.595 |

---

## 7. Price, Freight & Installments vs Review Score

**Correlation matrix:**

|                  |   total_price |   total_freight |   freight_ratio |   max_installments |   review_score |
|:-----------------|--------------:|----------------:|----------------:|-------------------:|---------------:|
| total_price      |         1     |           0.413 |          -0.297 |              0.313 |         -0.04  |
| total_freight    |         0.413 |           1     |           0.103 |              0.199 |         -0.089 |
| freight_ratio    |        -0.297 |           0.103 |           1     |             -0.188 |         -0.021 |
| max_installments |         0.313 |           0.199 |          -0.188 |              1     |         -0.032 |
| review_score     |        -0.04  |          -0.089 |          -0.021 |             -0.032 |          1     |

---

## 8. Product Listing Quality vs Review Score

|              |   avg_photos |   avg_desc_len |   avg_weight_g |   review_score |
|:-------------|-------------:|---------------:|---------------:|---------------:|
| avg_photos   |        1     |          0.121 |          0.029 |          0.015 |
| avg_desc_len |        0.121 |          1     |          0.058 |          0.011 |
| avg_weight_g |        0.029 |          0.058 |          1     |         -0.031 |
| review_score |        0.015 |          0.011 |         -0.031 |          1     |

---

## 9. Marketing Funnel → Seller Coverage

- `closed_deals_dataset` rows: 842
- Of those, sellers that also appear in `sellers_dataset`: 380 (45.1%)
- Of those, sellers with at least one actual order: 380 (45.1%)

---
