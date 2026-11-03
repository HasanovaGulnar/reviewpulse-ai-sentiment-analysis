"""Reusable inference and safe local analytics functions."""
from __future__ import annotations

import csv
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from src.config import LABEL_NAMES, MODEL_PATH, USAGE_LOG_PATH, ensure_directories


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model is missing. Run: python -m src.train")
    return joblib.load(MODEL_PATH)


def predict_reviews(model, texts: list[str]) -> pd.DataFrame:
    cleaned = [" ".join(str(text).split()) for text in texts]
    if not cleaned or any(not text for text in cleaned):
        raise ValueError("Each review must contain text.")
    probabilities = np.asarray(model.predict_proba(cleaned))
    classes = list(model.named_steps["classifier"].classes_)
    predictions = probabilities.argmax(axis=1)
    return pd.DataFrame(
        {
            "review": cleaned,
            "sentiment": [LABEL_NAMES[classes[index]] for index in predictions],
            "confidence": probabilities.max(axis=1),
        }
    )


def log_usage(action: str, review_count: int) -> None:
    ensure_directories()
    write_header = not USAGE_LOG_PATH.exists()
    with USAGE_LOG_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "action", "review_count"])
        if write_header:
            writer.writeheader()
        writer.writerow(
            {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "action": action, "review_count": review_count}
        )
