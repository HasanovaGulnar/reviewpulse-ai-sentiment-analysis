"""Download a reproducible Yelp review sample and create local data splits."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
from sklearn.model_selection import train_test_split

from src.config import (
    DATA_METADATA_PATH,
    RANDOM_SEED,
    RAW_BLOCK_DIR,
    RAW_DATA_PATH,
    SAMPLE_SIZE,
    SENTIMENT_LABELS,
    SOURCE_DATASET,
    SOURCE_URL,
    SPLIT_PATHS,
    ensure_directories,
)


def star_to_sentiment(star_label: int) -> str:
    """Map original Yelp labels 0..4 to negative, neutral, positive."""
    if star_label in (0, 1):
        return "negative"
    if star_label == 2:
        return "neutral"
    if star_label in (3, 4):
        return "positive"
    raise ValueError(f"Unexpected Yelp star label: {star_label}")


def sampled_block_ids(sample_size: int = SAMPLE_SIZE, seed: int = RANDOM_SEED) -> list[int]:
    if sample_size % 100:
        raise ValueError("sample_size must be divisible by 100 because the API returns blocks of 100 rows.")
    rng = np.random.default_rng(seed)
    return [int(item) for item in sorted(rng.choice(6500, size=sample_size // 100, replace=False))]


def download_sample(sample_size: int = SAMPLE_SIZE, seed: int = RANDOM_SEED) -> tuple[pd.DataFrame, list[int]]:
    """Fetch deterministic 100-row blocks from Yelp's public dataset-server API."""
    # Yelp's train split has 650,000 examples. Sampling block starts avoids a large download.
    block_ids = sampled_block_ids(sample_size, seed)
    records: list[dict] = []

    for position, block_id in enumerate(block_ids, start=1):
        cache_path = RAW_BLOCK_DIR / f"block_{block_id}.json"
        if cache_path.exists():
            records.extend(json.loads(cache_path.read_text(encoding="utf-8")))
            print(f"Using cached block {position}/{len(block_ids)}", flush=True)
            continue
        params = {
            "dataset": SOURCE_DATASET,
            "config": "yelp_review_full",
            "split": "train",
            "offset": int(block_id * 100),
            "length": 100,
        }
        # The public Dataset Server rate-limits rapid repeated requests. Backoff
        # keeps setup reliable without hiding a failed download.
        response = None
        for attempt in range(6):
            response = requests.get(SOURCE_URL, params=params, timeout=45)
            if response.status_code != 429:
                break
            wait_seconds = max(float(response.headers.get("Retry-After", 0)), 2 ** attempt)
            print(f"Rate-limited; retrying block {block_id} in {wait_seconds:.0f}s", flush=True)
            time.sleep(wait_seconds)
        assert response is not None
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("rows", [])
        if len(rows) != 100:
            raise RuntimeError(f"Expected 100 rows for block {block_id}; received {len(rows)}.")

        block_records = []
        for item in rows:
            row = item["row"]
            text = " ".join(str(row["text"]).split())
            if not text:
                continue
            block_records.append(
                {
                    "source_row_id": item["row_idx"],
                    "star_label": int(row["label"]) + 1,
                    "text": text,
                    "sentiment": star_to_sentiment(int(row["label"])),
                }
            )
        cache_path.write_text(json.dumps(block_records, ensure_ascii=False), encoding="utf-8")
        records.extend(block_records)
        print(f"Downloaded block {position}/{len(block_ids)}", flush=True)
        # Stay below the public endpoint's burst rate.
        time.sleep(0.75)

    frame = pd.DataFrame.from_records(records).drop_duplicates(subset="text")
    if len(frame) < 1000:
        raise RuntimeError("Downloaded sample is too small for the project requirement.")
    return frame.sample(frac=1, random_state=seed).reset_index(drop=True), block_ids


def save_splits(frame: pd.DataFrame, seed: int = RANDOM_SEED) -> dict[str, pd.DataFrame]:
    """Create 70/15/15 stratified train/validation/test splits."""
    train, remainder = train_test_split(
        frame, test_size=0.30, random_state=seed, stratify=frame["sentiment"]
    )
    validation, test = train_test_split(
        remainder, test_size=0.50, random_state=seed, stratify=remainder["sentiment"]
    )
    splits = {"train": train, "validation": validation, "test": test}
    for name, split in splits.items():
        split.sort_values("source_row_id").to_csv(SPLIT_PATHS[name], index=False, encoding="utf-8")
    return splits


def build_dataset(force: bool = False) -> None:
    ensure_directories()
    if RAW_DATA_PATH.exists() and not force:
        frame = pd.read_csv(RAW_DATA_PATH)
        blocks = sampled_block_ids()
        print(f"Using existing sample: {RAW_DATA_PATH}")
    else:
        frame, blocks = download_sample()
        frame.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8")

    splits = save_splits(frame)
    metadata = {
        "dataset": SOURCE_DATASET,
        "source_api": SOURCE_URL,
        "sample_size_requested": SAMPLE_SIZE,
        "sample_size_after_deduplication": int(len(frame)),
        "random_seed": RANDOM_SEED,
        "sampled_100_row_blocks": blocks,
        "label_mapping": {"1-2 stars": "negative", "3 stars": "neutral", "4-5 stars": "positive"},
        "split_proportions": {"train": 0.70, "validation": 0.15, "test": 0.15},
        "splits": {
            name: {"rows": int(len(split)), "class_distribution": split["sentiment"].value_counts().to_dict()}
            for name, split in splits.items()
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    DATA_METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata["splits"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Download a new deterministic sample.")
    args = parser.parse_args()
    build_dataset(force=args.force)
