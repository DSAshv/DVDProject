# Ashwanth: Product Pricing

## Focus
This analysis tests which product, pricing, freight, and listing-quality factors are associated with bad reviews after controlling the main comparison to on-time orders.

## Method
Master orders, products, and order items are joined. Delivered orders with reviews are retained; the highest-priced item represents multi-item orders. Price, freight ratio, weight, volume, photo count, description length, and item count are grouped into quantile or capped bins. Bad reviews are scores 1-2, and category analysis requires at least 200 orders.

## Graphs
- **Distribution panel:** eight histograms for price, freight ratio, weight, volume, photos, description length, product-name length, and item count. Log transforms reduce skew and capped counts keep extreme values readable.
- **Feature charts:** bar charts show bad-review rate by price, freight ratio, weight, volume, photo count, description length, and item count bins. Each compares groups of on-time orders to reveal product-level associations.
- **Feature ranking:** a horizontal correlation chart orders point-biserial correlations by absolute size; colors distinguish factors associated with more or fewer bad reviews.
- **Revenue ranking:** horizontal bars rank the top categories by revenue, with color indicating revenue tier and high bad-review categories highlighted.
- **Revenue-satisfaction quadrant:** a bubble scatter plot places category revenue on x, bad-review rate on y, and order volume in bubble size. Median thresholds create action quadrants.
- **All-category chart:** horizontal bars sort qualifying categories by bad-review rate while colors identify high or low revenue and satisfaction risk.

## Overall contribution
The analysis turns dissatisfaction into seller-controlled product actions: improve photos and descriptions, manage freight relative to item value, and prioritize high-revenue categories with elevated complaint rates.

## Conclusion
Delivery is still the strongest satisfaction factor, but listing quality and freight provide additional levers. The relationships are associative, not causal; the findings should guide prioritization and testing rather than prove that one product change causes better reviews.