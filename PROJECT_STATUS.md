# Capstone delivery status

## Proposal-to-product mapping

| Approved success criterion | Delivered evidence |
|---|---|
| At least 1,000 real labelled examples and reproducible splits | 2,000 real Yelp reviews; seed, source, blocks, label mapping and 70/15/15 split are in `reports/data_metadata.json`. |
| Per-class precision, recall and F1, plus macro F1 | `reports/metrics.json` and `reports/EVALUATION.md`; held-out test macro F1 is 0.664. |
| Single-review and batch CSV analysis | Streamlit tabs in `app.py`; sample input is in `examples/sample_reviews.csv`. |
| A working local demo and clear setup | `README.md`, `run_reviewpulse.ps1`, `MENTOR_CHECKLIST.md`, and automated verification scripts. |

## Public deployment and user test

| Requirement | Status | Evidence |
|---|---|---|
| Live public URL | Done (temporary) | `https://bargain-merry-corps-postal.trycloudflare.com`; permanent Streamlit Community Cloud path in `docs/DEPLOYMENT.md` |
| First-time-user instructions | Done | In-app onboarding box; README “First-time users (30 seconds)” |
| 3+ external testers | Pending | Invitation text in `docs/TESTER_MESSAGE.md`; tracking table in `docs/FEEDBACK.md` |
| Categorized feedback | Pending | Four categories and triage rules defined; rows pending submissions |
| At least 1 shipped fix | Partial | Fix 1 (low-confidence results) shipped from QA; the first tester-driven fix is pending the round |
| Before/after note | Partial | Format and Fix 1 in `docs/BEFORE_AFTER.md`; Fix 2 slot open |
| Uptime monitoring | Done | `.github/workflows/uptime.yml` checks `/_stcore/health` every 30 minutes |
| Unique session count | Done | Anonymous session id in `logs/usage.csv`; shown in the sidebar and Model & data tab |
| Lessons learned | Pending | `docs/LESSONS.md` fills after the round |

## Technical writeup and case study

| Requirement | Status | Evidence |
|---|---|---|
| Portfolio/LinkedIn tone | Done | `docs/index.md` written for a technical reader outside the program |
| 600–1000 words | Done | 949 words (verified by script) |
| Problem statement, 2–3 paragraphs | Done | "The problem" — 3 paragraphs, no project jargon |
| Legible, accurate architecture diagram | Done | `docs/architecture.svg` — training, runtime and operations; rendered live on the public page |
| 2+ non-obvious decisions with trade-offs | Done | Three: classical model vs transformer, committed artifact vs training at boot, three classes vs two |
| Honest results incl. limitations | Done | Per-class table, macro F1 0.664, neutral F1 0.43, uncalibrated confidence, Yelp-bound vocabulary |
| "What I'd improve" | Done | Five concrete next steps |
| Bonus: published publicly | Done | <https://hasanovagulnar.github.io/reviewpulse-ai-sentiment-analysis/> (GitHub Pages, source `main` / `docs`) |
| Bonus: screenshots | Done | `docs/images/app-onboarding.png`, `docs/images/app-result.png` (live app, 2× DPI) |
| Bonus: outside-reader confirmation | Pending | Ask one non-mentor to read the public page and confirm it is understandable without context |

## Verification completed locally

- `python -m src.data_pipeline` — passed; deterministic 2,000-review dataset and splits created.
- `python -m src.train` — passed; local model saved (714 KB) and metrics generated.
- `python -m unittest discover -s tests -v` — passed (12 tests).
- `python scripts/verify_project.py` — passed.
- `python scripts/ui_smoke.py` — passed; onboarding, example, analysis and feedback form.
- Public health check — `https://bargain-merry-corps-postal.trycloudflare.com/_stcore/health` returns `ok`.

## Honest limitation

This is a triage assistant, not an automated customer-service decision maker.
Its neutral class is notably weaker than its positive and negative classes; the
evaluation report makes that limitation explicit. The public link is a temporary
tunnel, and the external tester round has not yet been completed, so the
feedback table and the tester-driven fix are still open.
