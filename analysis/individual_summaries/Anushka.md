# Anushka: Regional Logistics

## Focus
This analysis examines whether delivery performance and customer satisfaction vary by customer state and by seller-state to customer-state route.

## Method
Orders, customers, sellers, items, and reviews are combined. Dates are converted to datetime, delivered orders are used for delivery-time measures, duplicate order IDs are removed, and only states with at least 100 orders and routes with at least 30 orders are ranked.

## Graphs
- **Top 10 states by late-delivery rate:** a descending bar chart of customer state versus the percentage of late orders. It identifies regions with the greatest delivery risk.
- **Bottom 10 states by average review score:** an ascending bar chart of customer state versus mean review score. It highlights regions with weaker customer experience.
- **Top 15 routes by late-delivery rate:** a descending bar chart of seller-state to customer-state routes versus late percentage. The minimum-volume filter prevents tiny routes from dominating.
- **Bottom 15 routes by review score:** a bar chart of routes versus average review score. It shows where poor satisfaction is geographically concentrated.

## Overall contribution
The work adds a geographic layer to the project. It helps separate broad delivery problems from state- or route-specific issues and complements the delivery-promise analysis.

## Conclusion
Regional and route rankings provide a practical way to prioritize logistics investigations. The readable notebook preserves the ranking design but not the executed results, so exact worst-performing regions should be taken from the final report before action.