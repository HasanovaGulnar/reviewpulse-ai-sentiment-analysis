# ReviewPulse

ReviewPulse is a local web app for small online sellers who want to understand
customer-review sentiment without manually reading every review. A seller can
analyze one review or upload a CSV batch. Each result is classified as
**negative**, **neutral**, or **positive**, with a confidence score and a batch
sentiment summary.

This capstone integrates two techniques from Weeks 1–7:

1. Classical NLP: TF-IDF features and Logistic Regression for review sentiment.
2. Product delivery: a Streamlit interface that a non-technical user can use.

It also includes local CSV usage logging as a small bonus feature.

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
python -m src.data_pipeline
python -m src.train
streamlit run app.py
```

The first data command downloads a deterministic 2,000-review sample from the
public `Yelp/yelp_review_full` dataset through Hugging Face's Dataset Server.
It saves the sample and reproducible 70/15/15 stratified splits locally. The
seed, sampled blocks, label distribution and source details are recorded in
`reports/data_metadata.json`.

Open the local Streamlit URL shown in the terminal, normally
`http://localhost:8501`.

## Use the app

### One review

Open **Single review**, paste a review, then choose **Analyze review**.

### Batch CSV

Open **Batch CSV**, upload any CSV that has a column containing review text,
select that column, then choose **Analyze batch**. Download the enriched CSV
when finished.

Example CSV:

```csv
review
The product arrived early and works perfectly.
The size was different from the description.
It is okay, but not special.
```

Usage counts and timestamps are stored locally in `logs/usage.csv`. Review text
is not logged.

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
