from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import DATA_METADATA_PATH, METRICS_PATH
from src.service import load_model, log_usage, predict_reviews

st.set_page_config(page_title="ReviewPulse", page_icon="💬", layout="wide")
st.title("💬 ReviewPulse")
st.caption("Local AI sentiment analysis for customer reviews — negative, neutral, or positive.")


@st.cache_resource
def get_model():
    return load_model()


def render_summary(results: pd.DataFrame) -> None:
    counts = results["sentiment"].value_counts().reindex(["positive", "neutral", "negative"], fill_value=0)
    left, middle, right = st.columns(3)
    left.metric("Positive", int(counts["positive"]))
    middle.metric("Neutral", int(counts["neutral"]))
    right.metric("Negative", int(counts["negative"]))
    st.bar_chart(counts)


try:
    model = get_model()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.code(".\\.venv\\Scripts\\python.exe -m src.data_pipeline\n.\\.venv\\Scripts\\python.exe -m src.train", language="powershell")
    st.stop()

single_tab, batch_tab, about_tab = st.tabs(["Single review", "Batch CSV", "Model & data"])

with single_tab:
    review = st.text_area("Paste one customer review", height=160, placeholder="Example: The delivery was quick and the product works perfectly.")
    if st.button("Analyze review", type="primary"):
        if not review.strip():
            st.warning("Enter a review first.")
        else:
            result = predict_reviews(model, [review])
            row = result.iloc[0]
            st.subheader(f"{row['sentiment'].title()} sentiment")
            st.metric("Confidence", f"{row['confidence']:.1%}")
            log_usage("single_review", 1)

with batch_tab:
    upload = st.file_uploader("Upload a CSV with one text column", type=["csv"])
    if upload is not None:
        try:
            batch = pd.read_csv(upload)
            if batch.empty:
                st.warning("The CSV is empty.")
            else:
                column = st.selectbox("Choose the review-text column", list(batch.columns))
                if st.button("Analyze batch", type="primary"):
                    texts = batch[column].fillna("").astype(str).tolist()
                    valid = [(index, text) for index, text in enumerate(texts) if text.strip()]
                    if not valid:
                        st.warning("No non-empty reviews were found.")
                    else:
                        predicted = predict_reviews(model, [text for _, text in valid])
                        output = batch.copy()
                        output["predicted_sentiment"] = pd.NA
                        output["confidence"] = pd.NA
                        for result_index, (source_index, _) in enumerate(valid):
                            output.loc[source_index, "predicted_sentiment"] = predicted.iloc[result_index]["sentiment"]
                            output.loc[source_index, "confidence"] = float(predicted.iloc[result_index]["confidence"])
                        st.success(f"Analyzed {len(valid)} of {len(batch)} rows.")
                        render_summary(predicted)
                        st.dataframe(output, width="stretch")
                        st.download_button("Download predictions CSV", output.to_csv(index=False).encode("utf-8"), "reviewpulse_predictions.csv", "text/csv")
                        log_usage("batch_csv", len(valid))
        except Exception as exc:
            st.error(f"Could not read or analyze this CSV: {exc}")

with about_tab:
    st.markdown("**Method:** TF-IDF text features + Logistic Regression. The model runs locally; uploaded reviews are not sent to an external API.")
    if DATA_METADATA_PATH.exists():
        metadata = json.loads(DATA_METADATA_PATH.read_text(encoding="utf-8"))
        st.json({"dataset": metadata["dataset"], "sample_rows": metadata["sample_size_after_deduplication"], "split_rows": {key: value["rows"] for key, value in metadata["splits"].items()}})
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        st.metric("Held-out test macro F1", f"{metrics['test']['macro_f1']:.3f}")
        st.dataframe(pd.DataFrame(metrics["test"]["per_class"]).T, width="stretch")
