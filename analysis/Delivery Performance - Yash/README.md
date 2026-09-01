# Delivery Performance (Yash)

**Q1.** How does delivery delay affect customer review scores?
**Q2.** Is it being slow, or breaking the promise, that angers customers?

Open **`Delivery_Performance_Analysis.ipynb`** and run it top to bottom. It is
self-contained: all the analysis and chart code is in the notebook itself, it
reads `processed_data/master_orders.csv` from the repo, and it writes every chart
into `figures/` and every table behind them into `outputs/`.

`Delivery_Performance_Report.pdf` is the same work written up.

## Answers

**Q1.** Delay does not wear satisfaction down gradually, it breaks at the promised
date. On time is 9.2% negative, late is 62.3%, so 6.8x worse. Late orders are 6.7%
of deliveries but 32.5% of all bad reviews.

**Q2.** Breaking the promise, clearly. An order that took over a month but arrived
when promised (21.2% negative) still beats one that was 1 to 2 days late (25.4%).

## Running it

Needs `processed_data/master_orders.csv` (built by `preprocess.py` at the repo
root) and `Dataset/` for one data-quality check. Only pandas, numpy and
matplotlib.

```bash
jupyter notebook "Delivery_Performance_Analysis.ipynb"
```

Jupyter is not in system python and Ubuntu blocks installing into it (PEP 668).
There is a venv at the repo root that adds jupyter while reusing the pandas and
matplotlib already installed:

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install jupyter nbconvert nbformat
```

## Decisions I had to defend

**Analysis**

- **One review per order.** The pipeline keeps the higher score where an order has
  two. I tried all four ways of picking. Only 202 of 98,673 orders have two
  different scores and the options span 0.097 pp, so it makes no difference.
- **Negative rate, never mean score.** Scores are lopsided, so a mean of 4.09
  describes nobody. Negative is 1 or 2 stars.
- **Error bars on every rate.** The smallest bucket has 75 orders. Wilson
  intervals, because the usual formula gives bars going below 0% at that size.
- **The 2x2 is reported but not relied on.** Late almost always means slow, so the
  box that would separate the two holds 187 orders with a 12-point error bar.
- **The most-late bucket says "cause not established" on the chart.** It turns less
  negative and its error bar clears the plateau, so it is not noise. Those orders
  have impossible transit times, about 124 days, which points at a delivery date
  filled in later, but I could not prove it so I did not invent a story.

**Design**

- **No distance chart, on purpose.** The check is in
  `outputs/q1_distance_control.csv` as a backup answer, but distance and routes are
  Anushka's question and neither of mine asks about geography. Worth passing that
  file to her.
- **One chart type per comparison.** Bars where you compare sizes, lines where the
  x axis is a length of time, a stacked bar where the answer is a share. Figure 4
  started as a histogram and did not work, because one bar held 93% of the on-time
  group and flattened everything else.
- **Only two colours, and each means something.** Blue is the normal group, red is
  always the bad outcome and never gets reused. Blue and red also stay apart for
  colour-blind readers, which red and green would not.
- **No second y axis.** Figure 3 is two charts on one shared scale. With separate
  scales a 14-point rise looks like a 57-point one.
- **Uneven bucket edges,** small near the promised date and wider further out,
  because almost everything happens in the first week.
- **Labels on the bars instead of a legend** where there is room. In Figure 4 each
  block carries its own number: the first version put "0.3%" just right of the
  sliver, which landed it on the blue block and read as if blue were 0.3%.

## Two things the rest of the team should know

Not in the report, because the report is a submission.

1. **`review_creation_date` in `master_orders.csv` is stored in two formats:**
   83,223 rows as `2018-08-11 00:00:00` and 15,450 as `2018-08-11`. Pandas infers
   one format and, with `errors="coerce"`, silently turns the other 84% into
   `NaT`. No warning, just a plausible-looking chart built on a sixth of the data.
   Parse it with `format="mixed"`. The notebook does this and asserts the null
   count did not move.
2. **`handling_days` still contains 1,359 negative values** (minimum -171 days).
   `preprocess.py`'s docstring says impossible timestamps are clipped, but the code
   only flags them. This affects Sahib's handling-time question, not mine.

Also worth someone fixing: `analysis_tab.py` reads `entry["html"]` but never
renders it, so only `pdf` and `notebook` become links on a member card.

## My local tooling, not uploaded

`build_notebook.py` generates and executes the notebook, and `build_report.py`
turns its output into the PDF. They are how I work, not part of the submission,
and nothing in the submission needs them. The notebook stands on its own.

## Not done

Review text (NLP) was considered and dropped. Only 41% of reviews have any text,
it is Portuguese, and the star rating already is the sentiment label. A keyword
comparison was prototyped and parked.
