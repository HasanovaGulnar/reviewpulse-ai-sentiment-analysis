from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
LOG_DIR = ROOT / "logs"

RAW_DATA_PATH = RAW_DIR / "yelp_review_sample.csv"
RAW_BLOCK_DIR = RAW_DIR / "yelp_blocks"
SPLIT_PATHS = {name: PROCESSED_DIR / f"{name}.csv" for name in ("train", "validation", "test")}
DATA_METADATA_PATH = REPORT_DIR / "data_metadata.json"
MODEL_PATH = MODEL_DIR / "reviewpulse_sentiment.joblib"
METRICS_PATH = REPORT_DIR / "metrics.json"
USAGE_LOG_PATH = LOG_DIR / "usage.csv"

RANDOM_SEED = 42
# This exceeds the proposal's 1,000-example minimum while keeping initial
# local setup practical on a student laptop.
SAMPLE_SIZE = 2000
SOURCE_DATASET = "Yelp/yelp_review_full"
SOURCE_URL = "https://datasets-server.huggingface.co/rows"

SENTIMENT_LABELS = {"negative": 0, "neutral": 1, "positive": 2}
LABEL_NAMES = {value: key for key, value in SENTIMENT_LABELS.items()}


def ensure_directories():
    for directory in (RAW_DIR, RAW_BLOCK_DIR, PROCESSED_DIR, MODEL_DIR, REPORT_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
