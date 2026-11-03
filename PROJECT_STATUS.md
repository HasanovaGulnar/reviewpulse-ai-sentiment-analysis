# Capstone delivery status

## Proposal-to-product mapping

| Approved success criterion | Delivered evidence |
|---|---|
| At least 1,000 real labelled examples and reproducible splits | 2,000 real Yelp reviews; seed, source, blocks, label mapping and 70/15/15 split are in `reports/data_metadata.json`. |
| Per-class precision, recall and F1, plus macro F1 | `reports/metrics.json` and `reports/EVALUATION.md`; held-out test macro F1 is 0.664. |
| Single-review and batch CSV analysis | Streamlit tabs in `app.py`; sample input is in `examples/sample_reviews.csv`. |
| A working local demo and clear setup | `README.md`, `run_reviewpulse.ps1`, `MENTOR_CHECKLIST.md`, and automated verification scripts. |

## Verification completed locally

- `python -m src.data_pipeline` — passed; deterministic 2,000-review dataset and splits created.
- `python -m src.train` — passed; local model saved and metrics generated.
- `python -m unittest discover -s tests -v` — passed (4 tests).
- `python scripts/verify_project.py` — passed.
- `python scripts/ui_smoke.py` — passed; Streamlit single-review flow returned Positive.

## Honest limitation

This is a triage assistant, not an automated customer-service decision maker.
Its neutral class is notably weaker than its positive and negative classes; the
evaluation report makes that limitation explicit.
