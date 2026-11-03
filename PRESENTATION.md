# ReviewPulse presentation guide (15–20 minutes)

## 1. Problem and user — 2 minutes

Small online sellers can receive too many reviews to read individually.
ReviewPulse helps them see the overall tone and find potential negative reviews
that may require attention.

## 2. Approved proposal and scope — 2 minutes

Show `proposal.md`. The project combines classical NLP and Streamlit. The scope
does not include a cloud API, user accounts, deployment, or a transformer model.

## 3. Data and evaluation — 4 minutes

Show `reports/data_metadata.json` and `reports/metrics.json`.

- Explain the Yelp 1–5-star source labels and the 3-class mapping.
- Show the 70/15/15 split and fixed seed.
- Explain precision, recall and F1 per class, then macro F1.
- State the actual test macro F1 from the report.

## 4. Live product walkthrough — 6 minutes

Start the app with `streamlit run app.py`.

1. Paste a clearly positive review in **Single review**.
2. Paste a clearly negative review.
3. Upload a small review CSV in **Batch CSV**.
4. Select the text column, run analysis, inspect the chart and download the
   predictions CSV.
5. Show the model/data tab and `logs/usage.csv`.

## 5. Hardest problem and honest reflection — 3 minutes

The hard problem was balancing data quality with a local, reliable demo.
Downloading and training on the entire Yelp corpus is unnecessarily heavy for
this product version. The solution was a seed-based 2,000-review sample and
explicitly saved splits. This is a conscious scope decision, not a hidden cut.

The model also uses star ratings as sentiment labels, so neutral is narrower
than everyday language use. The UI should be treated as decision support, not
an automated customer-service system.

## 6. Next steps — 2 minutes

Topic clustering, an urgent-review queue, an external tester, a separate review
domain for stronger evaluation, and optional public deployment.
