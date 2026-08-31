# EDA Report — Olist E-Commerce

## 0. Dataset Overview

| Metric | Value |
|--------|-------|
| Total orders | 99,441 |
| Reviewed orders | 98,673 |
| Delivered orders | 96,478 |
| Delivered + reviewed | 95,832 |
| Unique customers | 96,096 |
| Unique sellers | 3,088 |
| Date range | 2016-09-04 → 2018-10-17 |

**Order status breakdown:**
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

---
## 1. Review Score Distribution  (Yash · finding 01)

|   review_score |   pct_of_reviews |   count |
|---------------:|-----------------:|--------:|
|              1 |            11.47 |   11316 |
|              2 |             3.16 |    3121 |
|              3 |             8.23 |    8116 |
|              4 |            19.3  |   19044 |
|              5 |            57.84 |   57076 |

**Baseline negative rate (score ≤ 2):** 14.63% of 98,673 reviewed orders
Note: Distribution is bimodal — 1-star alone (11.5%) outweighs 2-star and 3-star combined.
This is why we report negative rate, not mean score.

---
## 2. The Promise Cliff — Delivery vs Promised Date  (Yash · finding 02)

| delay_bucket   |   orders |   negative_pct |   mean_score |
|:---------------|---------:|---------------:|-------------:|
| 30+ early      |     2712 |          10.8  |         4.26 |
| 15-30 early    |    32059 |           8.86 |         4.33 |
| 7-15 early     |    40973 |           8.91 |         4.31 |
| 3-7 early      |     9429 |          10.3  |         4.19 |
| 0-3 early      |     4270 |          11.59 |         4.11 |
| 0-3 late       |     1852 |          32.13 |         3.29 |
| 3-7 late       |     1748 |          67.51 |         2.11 |
| 7-15 late      |     1601 |          79.89 |         1.68 |
| 15-30 late     |      851 |          82.14 |         1.61 |
| 30+ late       |      329 |          67.78 |         2.06 |

**Key numbers (replicating Yash's report):**
- On-time orders: **9.2%** negative — flat across 60 days of earliness
- Late orders: **62.3%** negative — a 6.8× jump
- Late orders are **6.7%** of deliveries but **32.5%** of all negative reviews

---
## 3. Slow vs Broken Promise  (Yash · finding 03)

**Among on-time orders — effect of absolute delivery time:**
| delivery_bucket   |   orders |   negative_pct |   mean_score |
|:------------------|---------:|---------------:|-------------:|
| ≤7d               |    25875 |           7.42 |         4.42 |
| 8-14d             |    39684 |           8.72 |         4.32 |
| 15-21d            |    17056 |          10.62 |         4.18 |
| 22-30d            |     5873 |          14.42 |         3.96 |
| 31-45d            |      910 |          21.21 |         3.69 |

**Among late orders — effect of how late:**
| lateness_bucket   |   orders |   negative_pct |   mean_score |
|:------------------|---------:|---------------:|-------------:|
| 0-3d late         |     1852 |          32.13 |         3.29 |
| 3-7d late         |     1748 |          67.51 |         2.11 |
| 7-15d late        |     1601 |          79.89 |         1.68 |
| 15-30d late       |      851 |          82.14 |         1.61 |
| 30+ late          |      329 |          67.78 |         2.06 |

Being slow annoys (+8 pts across 70 days on-time). Breaking the promise enrages (+20 pts in first 3 days late).

---
## 4. Handling Time vs Transit Time  (Yash · finding 04)

Median seller handling time : 1.8 days (purchase → carrier)
Median carrier transit time : 7.1 days (carrier → customer)

**Negative rate by seller handling time:**
| handling_bucket   |   orders |   negative_pct |   mean_score |
|:------------------|---------:|---------------:|-------------:|
| ≤1d               |    27620 |           9.85 |         4.29 |
| 1-2d              |    22690 |          11.27 |         4.23 |
| 2-3d              |    14054 |          12.22 |         4.18 |
| 3-5d              |    16270 |          13.51 |         4.11 |
| 5-7d              |     7361 |          16.53 |         3.99 |
| 7-14d             |     4902 |          21.01 |         3.78 |
| 14+d              |     1576 |          41.5  |         3.01 |

**Negative rate by carrier transit time:**
| transit_bucket   |   orders |   negative_pct |   mean_score |
|:-----------------|---------:|---------------:|-------------:|
| ≤5d              |    29294 |           8.78 |         4.35 |
| 5-7d             |    16834 |           8.87 |         4.33 |
| 7-10d            |    18420 |           9.67 |         4.28 |
| 10-14d           |    13592 |          10.5  |         4.2  |
| 14-21d           |    10563 |          14.56 |         4.01 |
| 21-31d           |     4709 |          36.23 |         3.18 |
| 31+d             |     2379 |          71.21 |         1.97 |

---
## 5. Regional Logistics — Customer State  (Anushka)

**All states ranked by negative rate (min 50 orders):**
| customer_state   |   orders |   negative_pct |   mean_score |   median_delivery_days |   late_rate_pct |   avg_total_price |
|:-----------------|---------:|---------------:|-------------:|-----------------------:|----------------:|------------------:|
| AL               |      394 |          21.07 |         3.86 |                  22.31 |           20.81 |            196.47 |
| MA               |      712 |          19.94 |         3.83 |                  19.13 |           17.13 |            163.39 |
| SE               |      334 |          18.86 |         3.91 |                  17.99 |           14.97 |            166.69 |
| RJ               |    12211 |          18.26 |         3.97 |                  12.03 |           11.92 |            142.03 |
| PA               |      933 |          17.9  |         3.91 |                  21.06 |           10.72 |            183.24 |
| CE               |     1273 |          17.12 |         3.94 |                  18.17 |           13.67 |            171.86 |
| BA               |     3229 |          16.97 |         3.93 |                  16.89 |           11.89 |            151.81 |
| PI               |      471 |          16.14 |         3.99 |                  16.31 |           13.8  |            178.22 |
| AC               |       80 |          15    |         4.09 |                  18.36 |            3.75 |            199.14 |
| PB               |      512 |          14.84 |         4.08 |                  18.15 |           10.16 |            216.56 |
| PE               |     1579 |          14.82 |         4.08 |                  15.66 |            9.44 |            158.46 |
| ES               |     1969 |          13.76 |         4.08 |                  13.59 |           10.41 |            130.65 |
| MS               |      699 |          13.3  |         4.16 |                  13.94 |            9.73 |            164.79 |
| AM               |      144 |          13.19 |         4.24 |                  25.86 |            2.78 |            153.37 |
| GO               |     1946 |          13.1  |         4.11 |                  13.93 |            6.37 |            143.51 |
| DF               |     2070 |          13.04 |         4.14 |                  11.36 |            5.7  |            142.72 |
| SC               |     3519 |          12.96 |         4.13 |                  12.98 |            8.07 |            141.84 |
| RN               |      471 |          12.95 |         4.15 |                  16.05 |            9.13 |            173.29 |
| MT               |      879 |          12.74 |         4.15 |                  16.08 |            5.8  |            171.95 |
| TO               |      273 |          12.09 |         4.15 |                  15.88 |            9.89 |            177.04 |
| RO               |      242 |          11.98 |         4.17 |                  17.52 |            2.89 |            188.66 |
| RS               |     5327 |          11.88 |         4.19 |                  13.18 |            6.03 |            136.36 |
| MG               |    11285 |          11.71 |         4.19 |                  10.31 |            4.47 |            136.44 |
| PR               |     4900 |          10.84 |         4.24 |                  10.43 |            3.96 |            135.54 |
| SP               |    40273 |          10.63 |         4.25 |                   7.21 |            4.43 |            125.14 |
| AP               |       66 |           6.06 |         4.24 |                  24.22 |            3.03 |            201.95 |

### 5b. Seller-State → Customer-State Routes  (Anushka Q2)

**Top 20 worst seller → customer state routes (min 30 orders):**
|              |   orders |   negative_pct |   mean_score |   median_delivery_days |
|:-------------|---------:|---------------:|-------------:|-----------------------:|
| ('PR', 'AL') |       36 |          33.33 |         3.47 |                  26.46 |
| ('PR', 'CE') |       63 |          28.57 |         3.46 |                  19    |
| ('PR', 'MA') |       42 |          26.19 |         3.76 |                  21.02 |
| ('RJ', 'CE') |       54 |          24.07 |         3.65 |                  20.33 |
| ('SP', 'AL') |      253 |          23.72 |         3.73 |                  22.95 |
| ('SP', 'MA') |      487 |          22.18 |         3.72 |                  19.48 |
| ('DF', 'RJ') |       95 |          22.11 |         3.88 |                  11.21 |
| ('SC', 'BA') |       75 |          21.33 |         3.75 |                  17.24 |
| ('SP', 'RJ') |     8068 |          20.08 |         3.89 |                  12.79 |
| ('PR', 'RJ') |      950 |          20    |         3.9  |                  14.06 |
| ('SP', 'SE') |      208 |          19.71 |         3.82 |                  17.83 |
| ('PR', 'BA') |      141 |          19.15 |         3.82 |                  18.25 |
| ('PR', 'PA') |       54 |          18.52 |         4.07 |                  22.61 |
| ('SP', 'BA') |     2291 |          18.2  |         3.87 |                  17.62 |
| ('SP', 'RR') |       33 |          18.18 |         3.76 |                  26.2  |
| ('MA', 'SP') |      122 |          18.03 |         3.93 |                  13.39 |
| ('SP', 'PA') |      672 |          18.01 |         3.88 |                  20.89 |
| ('SC', 'RJ') |      465 |          17.85 |         3.96 |                  13.03 |
| ('PR', 'PB') |       40 |          17.5  |         4.03 |                  19.61 |
| ('DF', 'BA') |       35 |          17.14 |         3.94 |                  16.41 |

---
## 6. Seller Performance  (Kannan)

Total distinct sellers with delivered+reviewed orders: 2,956

**Supply-side concentration (top 148 sellers = top 5%):**
| Metric | Top 5% sellers | Rest 95% |
|--------|----------------|---------|
| Orders | 53.0% | 47.0% |
| GMV    | 45.8% | 54.2% |
| Negative reviews | 54.6% | 45.4% |

**Worst 10% of sellers with ≥20 orders (80 sellers):**
- Account for 14.1% of all bad orders, 6.9% of GMV
- Ratio: 2.0x bad orders per GMV point → strong intervention candidate

**Worst 20 individual sellers (min 20 orders):**
| primary_seller_id                |   n_orders |   negative_pct |   mean_score |   late_rate_pct |      gmv |
|:---------------------------------|-----------:|---------------:|-------------:|----------------:|---------:|
| 1ca7077d890b907f89be8c954a02686a |        107 |          59.81 |         2.39 |           16.82 | 12394.3  |
| 2eb70248d66e0e3ef83659f71b244378 |        182 |          47.8  |         2.78 |           10.99 | 37485.2  |
| a49928bcdf77c55c6d6e05e09a9b4ca5 |         94 |          39.36 |         3.06 |           22.34 |  8495.09 |
| 972d0f9cf61b499a4812cf0bfa3ad3c4 |         74 |          40.54 |         3.11 |           12.16 |  7342.28 |
| 2a1348e9addc1af5aaa619b1a3679d6b |         47 |          36.17 |         3.17 |           25.53 |  2811.35 |
| 54965bbe3e4f07ae045b90b0b8541f52 |         68 |          39.71 |         3.18 |           29.41 |  9647    |
| bbad7e518d7af88a0897397ffdca1979 |         65 |          38.46 |         3.25 |           16.92 |  4478.61 |
| d71d863e5ef30d94e440c11be17dcd8f |         20 |          40    |         3.25 |           15    |  8199.9  |
| 5058e8c1e82653974541e83690655b4a |         60 |          30    |         3.28 |           11.67 |  9974.06 |
| 602044f2c16190c2c6e45eb35c2e21cb |         45 |          33.33 |         3.33 |           15.56 |  3451.67 |
| 8444e55c1f13cd5c179851e5ca5ebd00 |         91 |          32.97 |         3.35 |            6.59 | 21667    |
| 070d165398b553f3b4b851c216b8a358 |         30 |          33.33 |         3.37 |           13.33 |  3312.08 |
| dc8798cbf453b7e0f98745e396cc5616 |         35 |          31.43 |         3.37 |            5.71 |  1733    |
| 6fd52c528dcb38be2eea044946b811f8 |         66 |          36.36 |         3.39 |           13.64 |  7625.68 |
| 712e6ed8aa4aa1fa65dab41fed5737e4 |         76 |          35.53 |         3.39 |           19.74 | 38796    |
| f76a3b1349b6df1ee875d1f3fa4340f0 |         23 |          30.43 |         3.39 |           30.43 |  4060.89 |
| 054694fa03fe82cec4b7551487331d74 |         20 |          30    |         3.4  |           30    |  8286.1  |
| a7f13822ceb966b076af67121f87b063 |         72 |          27.78 |         3.4  |            4.17 | 11840.7  |
| 835f0f7810c76831d6c7d24c7a646d4d |         41 |          29.27 |         3.41 |           26.83 |  4975.3  |
| 0b35c634521043bf4b47e21547b99ab5 |         48 |          35.42 |         3.42 |           14.58 | 14098.4  |

### 6b. Seller Size vs Negative Rate  (Kannan Q2 / Yash correction)

| size_bucket   |   n_sellers |   total_orders |   avg_negative_pct |
|:--------------|------------:|---------------:|-------------------:|
| 1-10          |        1794 |           6563 |              12.23 |
| 11-20         |         390 |           5708 |              12.66 |
| 21-50         |         366 |          11981 |              11.67 |
| 51-100        |         204 |          14583 |              12.19 |
| 101-200       |         119 |          16584 |              12.91 |
| 201+          |          83 |          40413 |              13.17 |

Spread is ~2 pts and runs the wrong way. Seller size is not a risk marker.

---
## 7. Seller Behaviour Drivers  (Sahib)

### 7a. Handling Time → Review Score

(Covered in section 4. Handling time is the seller-controllable half of wait.)

### 7b. Order Volume → Negative Rate

| vol_bucket   |   n_sellers |   total_orders |   avg_negative_pct |   avg_late_rate |
|:-------------|------------:|---------------:|-------------------:|----------------:|
| 1            |         537 |            537 |              13.22 |            8.38 |
| 2-5          |         812 |           2574 |              11.93 |            6.64 |
| 6-20         |         835 |           9160 |              12.08 |            6.57 |
| 21-50        |         366 |          11981 |              11.67 |            6.33 |
| 51-200       |         323 |          31167 |              12.46 |            6.13 |
| 201+         |          83 |          40413 |              13.17 |            7.13 |

### 7c. Freight Pricing → Review Score  (Sahib Q1)

| freight_ratio   |   orders |   negative_pct |   mean_score |
|:----------------|---------:|---------------:|-------------:|
| <10%            |    14815 |          12.48 |         4.2  |
| 10-20%          |    27504 |          12.22 |         4.18 |
| 20-30%          |    19521 |          12.47 |         4.16 |
| 30-50%          |    18478 |          13.5  |         4.12 |
| 50-100%         |    12124 |          13.1  |         4.13 |
| >100%           |     3055 |          15.22 |         4.04 |
Customers do not punish high freight cost — only late shipping (Yash finding 04, spread 1.3 pts).

### 7d. Where to Invest vs Intervene  (Sahib Q2)

Driver spread summary (best bucket negative rate → worst bucket):
- **Lateness (on-time vs late):** 9.2% → 62.3% = 53.1 pts
- **Delay days (0-3 late vs 30+ late):** 32.1% → 82.4% = 50.3 pts
- **Transit time (≤5d vs 31+d):** See section 4
- **Item price (decile 1 vs 10):** 13.0% → 16.3% = 3.7 pts
- **Payment type:** ~3.7 pts — indistinguishable
- **Installment count:** ~3.7 pts — confounded with price
- **Freight ratio:** ~1.3 pts — customers don't punish freight cost

---
## 8. Product & Pricing  (Ashwanth)

### 8a. Category: Revenue vs Satisfaction  (Ashwanth Q2)

**Top 20 categories by GMV:**
| product_category_name_english   |   orders |              gmv |   avg_review_score |   negative_pct |
|:--------------------------------|---------:|-----------------:|-------------------:|---------------:|
| health beauty                   |     8601 |      1.22468e+06 |               4.19 |          12.45 |
| watches gifts                   |     5454 |      1.15922e+06 |               4.07 |          14.81 |
| bed bath table                  |     9177 |      1.01359e+06 |               3.93 |          18.05 |
| sports leisure                  |     7486 | 948960           |               4.17 |          13.01 |
| computers accessories           |     6499 | 884761           |               3.99 |          16.94 |
| furniture decor                 |     6260 | 705997           |               3.96 |          17.9  |
| housewares                      |     5709 | 611636           |               4.11 |          14.18 |
| cool stuff                      |     3531 | 603221           |               4.2  |          11.85 |
| auto                            |     3792 | 571453           |               4.12 |          13.83 |
| garden tools                    |     3428 | 467301           |               4.09 |          14.93 |
| toys                            |     3774 | 466649           |               4.21 |          12.15 |
| baby                            |     2787 | 397301           |               4.08 |          14.94 |
| perfumery                       |     3076 | 388628           |               4.22 |          13.04 |
| telephony                       |     4069 | 307798           |               3.99 |          15.53 |
| office furniture                |     1244 | 265270           |               3.52 |          25.45 |
| stationery                      |     2251 | 222632           |               4.25 |          11.59 |
| pet shop                        |     1680 | 210727           |               4.22 |          12.06 |
| computers                       |      174 | 209919           |               4.22 |          11.73 |
| musical instruments             |      605 | 181668           |               4.22 |          11.94 |
| small appliances                |      604 | 181279           |               4.23 |          12.25 |

**Bottom 15 categories by avg review score (min 50 orders):**
| product_category_name_english           |   orders |              gmv |   avg_review_score |   negative_pct |
|:----------------------------------------|---------:|-----------------:|-------------------:|---------------:|
| office furniture                        |     1244 | 265270           |               3.52 |          25.45 |
| fixed telephony                         |      209 |  54715.2         |               3.76 |          23.02 |
| fashion male clothing                   |      105 |  10257.3         |               3.76 |          25    |
| audio                                   |      345 |  50290.9         |               3.84 |          21.51 |
| home confort                            |      390 |  57231.6         |               3.86 |          19.44 |
| furniture living room                   |      409 |  66169           |               3.93 |          17.14 |
| bed bath table                          |     9177 |      1.01359e+06 |               3.93 |          18.05 |
| unknown                                 |     1382 | 169652           |               3.94 |          19.41 |
| furniture decor                         |     6260 | 705997           |               3.96 |          17.9  |
| home construction                       |      481 |  81155.1         |               3.96 |          17.4  |
| construction tools safety               |      158 |  38744.2         |               3.97 |          17.58 |
| computers accessories                   |     6499 | 884761           |               3.99 |          16.94 |
| telephony                               |     4069 | 307798           |               3.99 |          15.53 |
| kitchen dining laundry garden furniture |      239 |  45279.1         |               4.03 |          13.6  |
| air conditioning                        |      242 |  52628.7         |               4.05 |          15.49 |

**High-GMV + above-baseline negative rate categories (the invest-vs-intervene quadrant):**
| product_category_name_english   |   orders |              gmv |   avg_review_score |   negative_pct |
|:--------------------------------|---------:|-----------------:|-------------------:|---------------:|
| watches gifts                   |     5454 |      1.15922e+06 |               4.07 |          14.81 |
| bed bath table                  |     9177 |      1.01359e+06 |               3.93 |          18.05 |
| computers accessories           |     6499 | 884761           |               3.99 |          16.94 |
| furniture decor                 |     6260 | 705997           |               3.96 |          17.9  |
| garden tools                    |     3428 | 467301           |               4.09 |          14.93 |
| baby                            |     2787 | 397301           |               4.08 |          14.94 |
| telephony                       |     4069 | 307798           |               3.99 |          15.53 |
| office furniture                |     1244 | 265270           |               3.52 |          25.45 |

### 8b. Non-Delivery Drivers  (Ashwanth Q1)

Correlations with review_score among delivered+reviewed orders:
|                  |   corr_with_review_score |
|:-----------------|-------------------------:|
| delivery_days    |                   -0.334 |
| transit_days     |                   -0.299 |
| delay_days       |                   -0.267 |
| handling_days    |                   -0.155 |
| n_items          |                   -0.123 |
| total_freight    |                   -0.09  |
| geo_distance     |                   -0.06  |
| total_price      |                   -0.035 |
| max_installments |                   -0.03  |
| freight_ratio    |                   -0.023 |

### 8c. Payment Type & Installments  (Ashwanth Q1 / Yash finding 04)

| dominant_payment_type   |   orders |   negative_pct |   mean_score |   avg_installments |
|:------------------------|---------:|---------------:|-------------:|-------------------:|
| credit_card             |    72616 |          12.82 |         4.16 |               3.52 |
| boleto                  |    19062 |          12.49 |         4.16 |               1    |
| voucher                 |     2675 |          13.76 |         4.12 |               1.47 |
| debit_card              |     1478 |          11.03 |         4.24 |               1    |

**Installment count buckets:**
| max_installments   |   orders |   negative_pct |   mean_score |
|:-------------------|---------:|---------------:|-------------:|
| 1                  |    46518 |          11.86 |         4.19 |
| 2-3                |    22015 |          12.85 |         4.15 |
| 4-6                |    15634 |          13.48 |         4.13 |
| 7-12               |    11486 |          15.11 |         4.08 |
| 13-24              |      176 |          20.45 |         3.9  |

---
## 9. Multi-Seller Orders — Unresolved Flag  (Yash · Section 06)

| | Single-seller | Multi-seller |
|--|---|---|
| Orders | 94,571 | 1,261 |
| Negative rate | 12.3% | 47.2% |
| Late rate | 6.7% | 1.0% |
| Median delay_days | -12.0 | -16.0 |

Multi-seller orders are 3.5× more likely to end in a negative review, yet show LESS lateness.
Likely cause: delivery timestamp records only one shipment; the order can look on-time while
the customer still waits for the second parcel. Do not use lateness figures for multi-seller
orders until this is confirmed. (Yash's Week-2 carry-over.)

---
## 10. Data Quality Flags  (Yash · Section 06)

- Orders where approval timestamp > carrier pickup: **1359** (impossible — excluded from timing analyses)
- Orders where customer delivery < carrier pickup:  **23** (impossible — excluded)
- Delivered orders with >100 day delivery:          **64** (real but extreme — charts should clip and note)
- Unknown product category: 610 products

---
## 11. Seasonal Pattern — Demand vs Capacity  (Fig 09 context)

| month   |   orders |   negative_pct |   late_rate_pct |
|:--------|---------:|---------------:|----------------:|
| 2016-10 |      262 |          16.41 |            0.76 |
| 2017-01 |      741 |          12.01 |            2.83 |
| 2017-02 |     1643 |          11.08 |            2.56 |
| 2017-03 |     2527 |          11.16 |            4.47 |
| 2017-04 |     2290 |          12.79 |            6.42 |
| 2017-05 |     3518 |          10.01 |            2.81 |
| 2017-06 |     3111 |          10.61 |            2.96 |
| 2017-07 |     3842 |           9.89 |            2.73 |
| 2017-08 |     4165 |           9.36 |            2.91 |
| 2017-09 |     4118 |          10.2  |            4.3  |
| 2017-10 |     4446 |          11.02 |            4.03 |
| 2017-11 |     7238 |          16.52 |           12.25 |
| 2017-12 |     5461 |          14.36 |            7.34 |
| 2018-01 |     7013 |          13.66 |            5.65 |
| 2018-02 |     6507 |          19.19 |           14.02 |
| 2018-03 |     6948 |          21.13 |           18.65 |
| 2018-04 |     6752 |          11.74 |            4.4  |
| 2018-05 |     6722 |          10.76 |            6.5  |
| 2018-06 |     6075 |           9.99 |            1.17 |
| 2018-07 |     6121 |           9.66 |            3.27 |
| 2018-08 |     6330 |           9.54 |            6.08 |

Correlation between monthly late rate and negative rate: **r = 0.80**
