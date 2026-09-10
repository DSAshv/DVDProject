# Kannan: Seller Performance

## Focus
This analysis identifies sellers responsible for unusually high dissatisfaction after accounting for category mix and delivery conditions.

## Method
Delivered, reviewed, single-seller orders are joined with items, products, sellers, and category translations. Duplicate reviews keep the latest record. Bad experience means a 1-2 star review. Seller rankings use minimum order thresholds and compare actual bad-review rates with expected rates from category and delivery.

## Graphs
- **Review-score distribution:** a bar chart counts scores 1-5, using contrasting colors for scores 1-2. It motivates tracking bad-review rate instead of only the average score.
- **Delay-effect and category charts:** bars compare bad-review rates across delay bands and categories against platform averages, showing major context effects.
- **Seller concentration curves:** cumulative seller share is compared with cumulative orders, bad reviews, and excess damage. The curves distinguish large sellers from sellers causing avoidable harm.
- **Definition comparison:** stacked horizontal bars compare the worst 5% by complaint count, excess complaints, and complaint rate across order, GMV, bad-review, and excess-damage shares.
- **Delivery test:** grouped bars compare offenders with other sellers within delay bands. A persistent gap on on-time orders indicates a seller-specific effect.
- **Expected-versus-actual scatter:** expected bad-review rate is plotted against actual rate; sellers above the equality line underperform their context.
- **Persistence heatmap:** seller bad-rate quartiles in the first and second history halves show whether poor performance persists over time.
- **Action chart:** a two-point trade-off compares coaching and delisting by GMV lost and expected improvement.

## Overall contribution
The work supplies seller accountability and intervention prioritization. It avoids blaming large sellers merely because they process more orders and separates seller-controlled problems from delivery and category effects.

## Conclusion
Seller quality is a secondary but meaningful lever. The recommended action is targeted coaching and diagnosis for the 77 repeatedly unusual sellers, rather than relying on raw complaint counts or immediately delisting sellers.