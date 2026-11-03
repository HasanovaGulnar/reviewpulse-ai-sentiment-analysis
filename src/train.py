"""Train and evaluate ReviewPulse's reproducible classical NLP classifier."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline

from src.config import (
    LABEL_NAMES,
    METRICS_PATH,
    MODEL_PATH,
    RANDOM_SEED,
    SENTIMENT_LABELS,
    SPLIT_PATHS,
    ensure_directories,
)


def load_split(name: str) -> pd.DataFrame:
    path = SPLIT_PATHS[name]
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run: python -m src.data_pipeline")
    return pd.read_csv(path)


def evaluate(model: Pipeline, frame: pd.DataFrame) -> dict:
    labels = list(SENTIMENT_LABELS.values())
    label_names = [LABEL_NAMES[label] for label in labels]
    predictions = model.predict(frame["text"])
    precision, recall, f1, support = precision_recall_fscore_support(
        frame["label"], predictions, labels=labels, zero_division=0
    )
    return {
        "rows": int(len(frame)),
        "macro_f1": float(f1_score(frame["label"], predictions, average="macro")),
        "class_distribution": {LABEL_NAMES[label]: int((frame["label"] == label).sum()) for label in labels},
        "per_class": {
            name: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, name in enumerate(label_names)
        },
        "confusion_matrix": confusion_matrix(frame["label"], predictions, labels=labels).tolist(),
        "classification_report": classification_report(
            frame["label"], predictions, labels=labels, target_names=label_names, zero_division=0
        ),
    }


def main() -> None:
    ensure_directories()
    train = load_split("train")
    validation = load_split("validation")
    test = load_split("test")

    label_map = SENTIMENT_LABELS
    for frame in (train, validation, test):
        frame["label"] = frame["sentiment"].map(label_map)

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=40_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    class_weight="balanced",
                    random_state=RANDOM_SEED,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    model.fit(train["text"], train["label"])
    joblib.dump(model, MODEL_PATH)

    metrics = {
        "model": "TF-IDF (1-2 grams) + Logistic Regression",
        "random_seed": RANDOM_SEED,
        "label_mapping": {"negative": 0, "neutral": 1, "positive": 2},
        "training": {"rows": int(len(train)), "class_distribution": train["sentiment"].value_counts().to_dict()},
        "validation": evaluate(model, validation),
        "test": evaluate(model, test),
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Validation macro F1: {metrics['validation']['macro_f1']:.3f}")
    print(f"Test macro F1: {metrics['test']['macro_f1']:.3f}")


if __name__ == "__main__":
    main()
