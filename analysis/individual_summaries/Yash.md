# Yash: Delivery Performance

## Focus
This analysis tests whether customer dissatisfaction is driven more by breaking the promised date or by taking longer overall to deliver.

## Method
Delivered, reviewed orders with valid delay values are analyzed from `master_orders.csv`. Bad reviews are scores 1-2. Duplicate-review rules are compared, Wilson confidence intervals are used, delay buckets are intentionally uneven, and undelivered reviewed orders are analyzed separately rather than silently included.

## Graphs
- **Promise cliff:** bars show negative-review rate across early, on-time, and late-delay buckets, with Wilson intervals, an all-orders baseline, and a day-zero divider. It shows the sharp change when the promise is broken.
- **Never-arrived comparison:** horizontal bars compare delivered groups with undelivered or no-date groups, including confidence intervals and sample sizes. It exposes dissatisfaction missed by delivered-order timing analysis.
- **Two slopes:** aligned lines compare delivery duration for on-time orders with lateness beyond promise for late orders on the same y-scale. It shows promise violation has the stronger association with bad reviews.
- **Review timing:** stacked horizontal shares split reviews into before- and after-arrival groups for promise-kept and promise-broken orders. It shows that many customers review late orders before the parcel arrives.
- **Distance control table:** late/on-time ratios are compared within distance quartiles as a robustness check, rather than as a separate chart.

## Overall contribution
This is the project's central customer-experience mechanism. It establishes promise reliability as a more useful operational target than raw delivery speed and identifies undelivered orders as an important blind spot.

## Conclusion
The strongest lever is a more honest and reliable delivery promise, supported by better exception handling. The result is associative rather than causal, so undelivered orders and distance-adjusted checks should remain part of follow-up analysis.