# ReviewPulse

ReviewPulse is a web app for small online sellers who want to understand
customer-review sentiment without manually reading every review. A seller can
analyze one review or upload a CSV batch. Each result is classified as
**negative**, **neutral**, or **positive**, with a confidence score, a
per-class probability breakdown and a batch sentiment summary.

**Live app:** <https://bargain-merry-corps-postal.trycloudflare.com>

> The link above is a Cloudflare quick tunnel from the development laptop. It is
> public and shareable while the app and tunnel are running, but the URL changes
> after a restart. The permanent deployment path is
> [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

**Case study:** [docs/index.md](docs/index.md) — the problem, an architecture
diagram, three trade-offs and the honest results (about 950 words).

## First-time users (30 seconds)

1. **Try it** — click an example (or paste an English review) and press
   **Analyze review**. You get a label, a confidence score and the probability
   for each class.
2. **Batch CSV** — download the example CSV, upload it, choose the text column
   and press **Analyze batch**. The enriched CSV is downloadable.
3. **Feedback** — describe anything broken, confusing or missing. The app is
   being tested, not launched.

The model was trained on 2,000 English Yelp reviews. Held-out test macro F1 is
**0.664**, and `neutral` is the weakest class (F1 0.43). The **Model & data** tab
shows per-class results, the confusion matrix and an explicit limitations list —
read it before trusting a label.

This capstone integrates two techniques from Weeks 1–7:

1. Classical NLP: TF-IDF features and Logistic Regression for review sentiment.
2. Product delivery: a Streamlit interface that a non-technical user can use.

It also includes anonymous session logging, an in-app feedback form, and short
error references for failed analyses.

## Feedback from real users

The **Feedback** tab records a category (bug / confusion / feature request /
other), the page, the message and an anonymous session id. The question set,
triage rules, tracking table and a Google Apps Script backend are in
[docs/FEEDBACK.md](docs/FEEDBACK.md). Tester outreach text is in
[docs/TESTER_MESSAGE.md](docs/TESTER_MESSAGE.md), and shipped fixes are
documented before/after in [docs/BEFORE_AFTER.md](docs/BEFORE_AFTER.md).

## Demo flow

```text
Seller review / CSV
        ↓
Streamlit UI → saved TF-IDF + Logistic Regression model
        ↓
Sentiment + confidence → batch summary + downloadable CSV
```

## Technology

- Python 3.13
- scikit-learn: TF-IDF and Logistic Regression
- Streamlit: local user interface
- pandas: CSV handling and analysis
- Yelp Review Full dataset: real labelled reviews

The original Yelp labels are mapped deliberately: 1–2 stars → negative, 3
stars → neutral, and 4–5 stars → positive. The model runs locally and does not
send uploaded review text to an external API.

## Setup

Run these commands from the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.data_pipeline   # only to rebuild the dataset
python -m src.train           # only to rebuild the model artifact
streamlit run app.py
```

The trained artifact (`models/reviewpulse_sentiment.joblib`, 714 KB) is
committed, so deployment does **not** need the data pipeline or a training run.
Run those two commands only to reproduce the artifact. They require Python 3.13
and scikit-learn 1.7.2, the versions used to build the committed model.

The data command downloads a deterministic 2,000-review sample from the public
`Yelp/yelp_review_full` dataset through Hugging Face's Dataset Server. It saves
the sample and reproducible 70/15/15 stratified splits locally. The seed, sampled
blocks, label distribution and source details are recorded in
`reports/data_metadata.json`.

Open the local Streamlit URL shown in the terminal, normally
`http://localhost:8501`.

## Use the app

### One review

Open **Try it**, click an example or paste your own review, then choose
**Analyze review**. The result shows the winning label, its confidence, and the
probability for all three classes. Low-confidence results carry a warning.

### Batch CSV

Open **Batch CSV**, download the example CSV if you need a starting point,
upload any CSV that has a column containing review text, select that column, then
choose **Analyze batch**. Download the enriched CSV when finished. Batches are
capped at 5,000 rows so a public instance stays responsive.

Example CSV:

```csv
review
The product arrived early and works perfectly.
The size was different from the description.
It is okay, but not special.
```

Anonymous usage events (session start, single/batch analysis, review counts) are
stored in `logs/usage.csv`; feedback goes to `logs/feedback.csv` and errors to
`logs/errors.csv`. Review text is never logged.

## Reproducibility and evaluation

The data seed is 42. `python -m src.train` saves:

- `models/reviewpulse_sentiment.joblib`
- `reports/metrics.json`: validation/test precision, recall, F1 per class,
  macro F1, class distributions and confusion matrix

Run automated checks:

```powershell
python -m unittest discover -s tests -v
python scripts/verify_project.py
python scripts/ui_smoke.py
```

The latest local training run achieved test macro F1 **0.664**. Class-level
results and the confusion matrix are in [reports/EVALUATION.md](reports/EVALUATION.md).

The suite has 12 unit tests plus a non-interactive Streamlit smoke test that
exercises the example button, the single-review path and the feedback form.

## Deployment and monitoring

- **Deployment:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) covers Streamlit
  Community Cloud (permanent URL, Python 3.13, secrets), a Cloudflare quick
  tunnel (the current temporary link) and Hugging Face Spaces, plus a
  troubleshooting table for the common build failures.
- **Uptime:** `.github/workflows/uptime.yml` pings `/_stcore/health` every 30
  minutes. Set the repository variable `REVIEWPULSE_APP_URL` to the public URL.
  For stricter checks, a free UptimeRobot monitor works without code changes.
- **Unique sessions:** every browser session gets a random id and one
  `session_start` row. The sidebar and **Model & data** tab show unique
  sessions, analyses and review counts for the running instance. On a hosted
  instance these counters reset when the app restarts; the optional webhook in
  `docs/FEEDBACK.md` makes them durable.
- **Errors:** failed predictions are logged with a short reference id that the
  app shows to the tester, so a report can be matched to a log line.

## Public deployment and user test

| Requirement | Status |
|---|---|
| Live public URL | ✅ temporary Cloudflare tunnel; permanent Streamlit Cloud path documented |
| First-time-user onboarding | ✅ in-app box + README “30 seconds” section |
| In-app feedback form | ✅ categorized, anonymous session id, local + webhook backends |
| 3+ external testers | ⏳ invite sent; feedback table ready in `docs/FEEDBACK.md` |
| Categorized feedback | ⏳ categories and triage rules defined; rows pending testers |
| At least 1 shipped fix | ✅ Fix 1 (low-confidence results) in `docs/BEFORE_AFTER.md`; ⏳ first tester-driven fix pending |
| Before/after note | ✅ format and Fix 1 documented |
| Uptime monitoring | ✅ scheduled health check |
| Unique session count | ✅ sidebar + Model & data tab |
| Lessons learned | ⏳ `docs/LESSONS.md` fills after the round |

## Project scope and reflection

The approved proposal is in [proposal.md](proposal.md). The implementation
matches its four success criteria: real labelled data with a reproducible split,
reported evaluation, a live single/batch app, and clear setup instructions.
The requirement-by-requirement delivery evidence is in
[PROJECT_STATUS.md](PROJECT_STATUS.md).

The main issue during development was downloading the complete 650,000-row Yelp
training set for a small local demo. It was deliberately cut to a deterministic
2,000-row sample fetched in reproducible blocks. This keeps the app practical
on a student laptop while exceeding the 1,000-example requirement. The tradeoff
is that metrics are for the sampled data, not the full corpus.

With two more weeks, I would add review-topic clustering, an "urgent negative"
queue, authentication, privacy controls for multi-user deployments, and a
hold-out dataset from a second review domain.

## Presentation

Use [PRESENTATION.md](PRESENTATION.md) for the 15–20 minute mentor walkthrough.
