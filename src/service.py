"""Reusable inference and safe local analytics functions."""
from __future__ import annotations

import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.config import (
    APP_VERSION,
    ERROR_LOG_PATH,
    FEEDBACK_LOG_PATH,
    LABEL_NAMES,
    MODEL_PATH,
    SENTIMENT_LABELS,
    USAGE_LOG_PATH,
    ensure_directories,
)

USAGE_FIELDS = ["timestamp_utc", "session_id", "action", "review_count", "app_version"]
FEEDBACK_FIELDS = ["timestamp_utc", "session_id", "category", "message", "contact", "page", "app_version"]
ERROR_FIELDS = ["timestamp_utc", "error_id", "session_id", "context", "error_type", "message", "app_version"]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "The trained model is missing from this checkout. "
            "Run: python -m src.data_pipeline && python -m src.train"
        )
    return joblib.load(MODEL_PATH)


def predict_reviews(model, texts: list[str]) -> pd.DataFrame:
    """Return one row per review with the label, confidence and class probabilities."""
    cleaned = [" ".join(str(text).split()) for text in texts]
    if not cleaned or any(not text for text in cleaned):
        raise ValueError("Each review must contain text.")
    probabilities = np.asarray(model.predict_proba(cleaned))
    classes = list(model.named_steps["classifier"].classes_)
    predictions = probabilities.argmax(axis=1)
    result = pd.DataFrame(
        {
            "review": cleaned,
            "sentiment": [LABEL_NAMES[classes[index]] for index in predictions],
            "confidence": probabilities.max(axis=1),
        }
    )
    for label, code in SENTIMENT_LABELS.items():
        if code in classes:
            result[f"p_{label}"] = probabilities[:, classes.index(code)]
    return result


def new_session_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_csv(path: Path, fieldnames: list[str], row: dict) -> bool:
    """Append one row. Returns False instead of breaking the app if disk is read-only."""
    try:
        ensure_directories()
        write_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        return True
    except OSError:
        return False


def log_usage(action: str, review_count: int, session_id: str = "") -> bool:
    return _append_csv(
        USAGE_LOG_PATH,
        USAGE_FIELDS,
        {
            "timestamp_utc": _now(),
            "session_id": session_id,
            "action": action,
            "review_count": int(review_count),
            "app_version": APP_VERSION,
        },
    )


def log_feedback(record: dict) -> bool:
    return _append_csv(
        FEEDBACK_LOG_PATH,
        FEEDBACK_FIELDS,
        {"timestamp_utc": _now(), "app_version": APP_VERSION, **record},
    )


def log_error(context: str, error: BaseException, session_id: str = "") -> str | None:
    """Record an error and return a short reference id the tester can quote."""
    error_id = uuid.uuid4().hex[:8]
    saved = _append_csv(
        ERROR_LOG_PATH,
        ERROR_FIELDS,
        {
            "timestamp_utc": _now(),
            "error_id": error_id,
            "session_id": session_id,
            "context": context,
            "error_type": type(error).__name__,
            "message": str(error)[:500],
            "app_version": APP_VERSION,
        },
    )
    return error_id if saved else None


def read_usage_summary(path: Path | None = None) -> dict:
    """Count unique sessions and analyses recorded by this instance."""
    summary = {"sessions": 0, "analyses": 0, "reviews": 0, "available": False}
    target = path or USAGE_LOG_PATH
    if not target.exists():
        return summary
    try:
        frame = pd.read_csv(target)
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return summary
    if frame.empty:
        return summary
    summary["available"] = True
    if "session_id" in frame.columns:
        starts = frame.loc[frame["action"] == "session_start", "session_id"]
        summary["sessions"] = int(starts.dropna().nunique())
    if "action" in frame.columns:
        summary["analyses"] = int((frame["action"].isin(["single_review", "batch_csv"])).sum())
    if "review_count" in frame.columns:
        summary["reviews"] = int(pd.to_numeric(frame["review_count"], errors="coerce").fillna(0).sum())
    return summary
