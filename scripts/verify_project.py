"""Fast local readiness check for a mentor demo."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DATA_METADATA_PATH, METRICS_PATH, MODEL_PATH, SPLIT_PATHS
from src.service import load_model, predict_reviews


def main() -> None:
    required = [DATA_METADATA_PATH, METRICS_PATH, MODEL_PATH, *SPLIT_PATHS.values()]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required project files:\n- " + "\n- ".join(missing))

    metadata = json.loads(DATA_METADATA_PATH.read_text(encoding="utf-8"))
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    model = load_model()
    sample = predict_reviews(model, ["The product arrived early and works perfectly."])

    print("ReviewPulse is ready for a local demo.")
    print(f"Dataset sample: {metadata['sample_size_after_deduplication']} real Yelp reviews")
    print(f"Test macro F1: {metrics['test']['macro_f1']:.3f}")
    print(f"Smoke prediction: {sample.iloc[0]['sentiment']} ({sample.iloc[0]['confidence']:.1%})")


if __name__ == "__main__":
    main()
