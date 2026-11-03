# Mentor demo checklist

## Before the meeting

```powershell
cd C:\Users\User\capstone-review-pulse
.\.venv\Scripts\python.exe scripts\verify_project.py
.\.venv\Scripts\python.exe scripts\ui_smoke.py
.\run_reviewpulse.ps1
```

If PowerShell blocks the launcher script, use this one-session setting first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Open the local address printed by Streamlit, normally `http://localhost:8501`.

## Core flow to verify live

1. On **Single review**, paste: `The product arrived early and works perfectly.`
   The app should return Positive.
2. Paste: `The packaging was damaged and customer support never replied.`
   The app should return Negative.
3. Open **Batch CSV**, upload `examples/sample_reviews.csv`, select `review`,
   then choose **Analyze batch**.
4. Confirm the three sentiment counts, table, and CSV download button appear.
5. Open **Model & data**. Confirm the local dataset summary and held-out macro
   F1 are visible.
6. Inspect `reports/metrics.json` for complete per-class precision, recall and
   F1, `reports/data_metadata.json` for seed/split provenance, and
   `logs/usage.csv` for local usage counts.

## Presentation evidence

- Approved plan: `proposal.md`
- Product setup and limitations: `README.md`
- Evaluation: `reports/EVALUATION.md` and `reports/metrics.json`
- Presentation agenda: `PRESENTATION.md`
