from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.config import APP_VERSION, DATA_METADATA_PATH, METRICS_PATH, REPO_URL, ROOT, ROOT
from src.feedback import (
    CATEGORY_CHOICES,
    PAGE_CHOICES,
    feedback_form_url,
    send_event,
    submit_feedback,
    validate_feedback,
    webhook_url,
)
from src.service import (
    load_model,
    log_error,
    log_usage,
    new_session_id,
    predict_reviews,
    read_usage_summary,
)

MAX_BATCH_ROWS = 5000
MAX_REVIEW_CHARS = 5000

EXAMPLES = {
    "Positive · delivery": "The product arrived early and works exactly as described.",
    "Negative · support": "The packaging was damaged and customer support never replied.",
    "Mixed · neutral": "It is acceptable for the price, but the quality is average.",
    "Sarcastic": "Great, it broke after two days. Exactly what I paid for.",
}

SENTIMENT_EMOJI = {"positive": "🟢", "neutral": "🟡", "negative": "🔴"}

st.set_page_config(page_title="ReviewPulse — review sentiment", page_icon="💬", layout="wide")


@st.cache_resource(show_spinner="Loading the sentiment model…")
def get_model():
    return load_model()


@st.cache_data(ttl=15)
def usage_summary() -> dict:
    return read_usage_summary()


def start_session() -> None:
    if "session_id" in st.session_state:
        return
    st.session_state.session_id = new_session_id()
    log_usage("session_start", 0, st.session_state.session_id)
    send_event("session_start", {"session_id": st.session_state.session_id, "app_version": APP_VERSION})


def analyze(model, texts: list[str], context: str):
    """Predict with an error path that gives the tester something actionable."""
    try:
        return predict_reviews(model, texts)
    except Exception as exc:  # noqa: BLE001 - the app must not crash on one bad input
        error_id = log_error(context, exc, st.session_state.session_id)
        reference = f" Reference: {error_id}." if error_id else ""
        st.error(f"Something went wrong while analyzing this input.{reference} Please report it in the Feedback tab.")
        return None


def render_summary(results: pd.DataFrame) -> None:
    counts = results["sentiment"].value_counts().reindex(["negative", "neutral", "positive"], fill_value=0)
    left, middle, right = st.columns(3)
    left.metric("🔴 Negative", int(counts["negative"]))
    middle.metric("🟡 Neutral", int(counts["neutral"]))
    right.metric("🟢 Positive", int(counts["positive"]))
    st.bar_chart(counts.rename("reviews"))


start_session()

st.title("💬 ReviewPulse")
st.caption("Paste a customer review and get **negative / neutral / positive** with a confidence score.")

with st.container(border=True):
    st.markdown("#### First time here? It takes 30 seconds")
    first, second, third = st.columns(3)
    first.markdown("**1 · Pick a review**\n\nUse an example or paste your own English review in **Try it**.")
    second.markdown("**2 · Analyze**\n\nYou get a label, a confidence score, and the probability for each class.")
    third.markdown("**3 · Tell us what broke**\n\nOpen **Feedback** and describe anything confusing or missing. This app is being tested, not launched.")
    st.caption(
        "Privacy: review text is processed by this app only and is never sent to an external AI API. "
        "Feedback you submit is saved with an anonymous session id."
    )

try:
    model = get_model()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.code("python -m src.data_pipeline\npython -m src.train", language="powershell")
    st.stop()
except Exception as exc:  # noqa: BLE001 - a broken artifact must not show a raw traceback
    error_id = log_error("model_load", exc, st.session_state.session_id)
    st.error(
        "The model artifact could not be loaded. It may have been built with a different "
        f"scikit-learn or Python version.{f' Reference: {error_id}.' if error_id else ''}"
    )
    st.code("python -m src.train", language="powershell")
    st.stop()

with st.sidebar:
    st.markdown("### About this test")
    st.markdown(
        "ReviewPulse is a capstone project being tested by real users. "
        "The goal is to find what breaks before calling it finished."
    )
    summary = usage_summary()
    st.metric("Unique sessions (this instance)", summary["sessions"])
    st.caption("Counted from `logs/usage.csv`. On a hosted deployment this file resets when the app restarts.")
    st.divider()
    st.markdown(f"**Build** v{APP_VERSION}")
    st.markdown(f"[Source code]({REPO_URL}) · [Feedback guide]({REPO_URL}/blob/main/docs/FEEDBACK.md)")

single_tab, batch_tab, about_tab, feedback_tab = st.tabs(["Try it", "Batch CSV", "Model & data", "Feedback"])

with single_tab:
    st.markdown("**No review handy? Pick an example:**")
    example_columns = st.columns(len(EXAMPLES))
    for column, (label, text) in zip(example_columns, EXAMPLES.items()):
        if column.button(label, key=f"example_{label[:8]}", use_container_width=True):
            st.session_state.review_text = text

    review = st.text_area(
        "Customer review",
        key="review_text",
        height=160,
        max_chars=MAX_REVIEW_CHARS,
        placeholder="Example: The delivery was quick and the product works perfectly.",
    )

    if st.button("Analyze review", type="primary", key="analyze_single"):
        if not review.strip():
            st.warning("Enter a review first — or click one of the examples above.")
        else:
            result = analyze(model, [review], "single_review")
            if result is not None:
                row = result.iloc[0]
                sentiment = row["sentiment"]
                left, right = st.columns([1, 2])
                with left:
                    st.subheader(f"{SENTIMENT_EMOJI.get(sentiment, '•')} {sentiment.title()} sentiment")
                    st.metric("Confidence", f"{row['confidence']:.1%}")
                with right:
                    probabilities = pd.DataFrame(
                        {"probability": [row.get(f"p_{label}", 0.0) for label in ("negative", "neutral", "positive")]},
                        index=["negative", "neutral", "positive"],
                    )
                    st.bar_chart(probabilities, horizontal=True)
                if row["confidence"] < 0.5:
                    st.warning(
                        "Low confidence — the model is unsure about this one. "
                        "Treat the label as a hint, not a verdict."
                    )
                st.caption(
                    "Confidence is the model's probability for the winning class, not a guarantee. "
                    "The neutral class is the weakest (test F1 0.43), and negation or sarcasm often flips the result."
                )
                log_usage("single_review", 1, st.session_state.session_id)
                send_event(
                    "analysis",
                    {
                        "session_id": st.session_state.session_id,
                        "action": "single",
                        "sentiment": sentiment,
                        "confidence": round(float(row["confidence"]), 3),
                        "length": len(review),
                    },
                )

with batch_tab:
    st.markdown(
        "Upload a CSV with one review per row. The app adds `predicted_sentiment` and `confidence` columns "
        "and lets you download the result."
    )
    with (ROOT / "examples" / "sample_reviews.csv").open("rb") as sample_file:
        st.download_button(
            "Download the example CSV",
            sample_file.read(),
            "sample_reviews.csv",
            "text/csv",
            key="download_example",
        )

    upload = st.file_uploader("Upload a CSV", type=["csv"])
    if upload is not None:
        try:
            batch = pd.read_csv(upload)
        except Exception as exc:  # noqa: BLE001 - a malformed CSV is a user error, not a crash
            log_error("batch_read", exc, st.session_state.session_id)
            st.error("This file could not be read as a CSV. Check the delimiter and encoding, then try again.")
            batch = None

        if batch is not None:
            if batch.empty:
                st.warning("The CSV is empty.")
            else:
                if len(batch) > MAX_BATCH_ROWS:
                    st.warning(
                        f"The file has {len(batch):,} rows. Only the first {MAX_BATCH_ROWS:,} are analyzed "
                        "so the public app stays responsive."
                    )
                    batch = batch.head(MAX_BATCH_ROWS).copy()
                st.caption(f"{len(batch):,} rows · {len(batch.columns)} columns")
                st.dataframe(batch.head(5), width="stretch")

                default_column = 0
                for index, name in enumerate(batch.columns):
                    if str(name).strip().lower() in {"review", "text", "comment", "content", "feedback"}:
                        default_column = index
                        break
                column = st.selectbox("Choose the review-text column", list(batch.columns), index=default_column)

                if st.button("Analyze batch", type="primary", key="analyze_batch"):
                    texts = batch[column].fillna("").astype(str).tolist()
                    valid = [(index, text) for index, text in enumerate(texts) if text.strip()]
                    if not valid:
                        st.warning("No non-empty reviews were found in that column.")
                    else:
                        predicted = analyze(model, [text for _, text in valid], "batch_csv")
                        if predicted is not None:
                            output = batch.copy()
                            output["predicted_sentiment"] = pd.NA
                            output["confidence"] = pd.NA
                            for result_index, (source_index, _) in enumerate(valid):
                                output.loc[source_index, "predicted_sentiment"] = predicted.iloc[result_index]["sentiment"]
                                output.loc[source_index, "confidence"] = float(predicted.iloc[result_index]["confidence"])
                            st.success(f"Analyzed {len(valid)} of {len(batch)} rows.")
                            render_summary(predicted)
                            st.dataframe(output, width="stretch")
                            st.download_button(
                                "Download predictions CSV",
                                output.to_csv(index=False).encode("utf-8"),
                                "reviewpulse_predictions.csv",
                                "text/csv",
                            )
                            log_usage("batch_csv", len(valid), st.session_state.session_id)
                            send_event(
                                "analysis",
                                {
                                    "session_id": st.session_state.session_id,
                                    "action": "batch",
                                    "rows": len(valid),
                                },
                            )

with about_tab:
    st.markdown(
        "**Method:** TF-IDF features (1–2 word grams, 40k vocabulary) + Logistic Regression. "
        "The model is trained on 2,000 real English Yelp reviews mapped to three classes: "
        "1–2 stars → negative, 3 stars → neutral, 4–5 stars → positive. It runs locally in this app."
    )

    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        test = metrics["test"]
        confusion = test["confusion_matrix"]
        accuracy = sum(confusion[i][i] for i in range(len(confusion))) / max(sum(map(sum, confusion)), 1)

        first, second, third = st.columns(3)
        first.metric("Held-out test macro F1", f"{test['macro_f1']:.3f}")
        second.metric("Held-out test accuracy", f"{accuracy:.1%}")
        third.metric("Training reviews", f"{metrics['training']['rows']:,}")

        st.markdown("**Per-class results on the held-out test split**")
        per_class = pd.DataFrame(test["per_class"]).T[["precision", "recall", "f1", "support"]]
        per_class.index.name = "class"
        for column_name in ("precision", "recall", "f1"):
            per_class[column_name] = per_class[column_name].astype(float).round(3)
        per_class["support"] = per_class["support"].astype(int)
        st.dataframe(per_class, width="stretch")

        with st.expander("Confusion matrix (rows = true, columns = predicted)"):
            labels = ["negative", "neutral", "positive"]
            st.dataframe(
                pd.DataFrame(confusion, index=labels, columns=[f"pred. {label}" for label in labels]),
                width="stretch",
            )

    if DATA_METADATA_PATH.exists():
        metadata = json.loads(DATA_METADATA_PATH.read_text(encoding="utf-8"))
        st.markdown("**Dataset**")
        st.json(
            {
                "source": metadata["dataset"],
                "sample_rows": metadata["sample_size_after_deduplication"],
                "random_seed": metadata["random_seed"],
                "split_rows": {name: value["rows"] for name, value in metadata["splits"].items()},
            },
            expanded=False,
        )

    st.markdown("**What this model does not do**")
    st.markdown(
        "- It does not understand sarcasm reliably: *\"Great, it broke after two days\"* often reads as positive.\n"
        "- Negation is fragile: *\"not good\"* can still land on positive.\n"
        "- It is trained on English Yelp reviews, not on your product domain or language.\n"
        "- `neutral` is the weakest class (F1 0.43); a 3-star review is often split between classes.\n"
        "- Confidence is a probability from this model, not a calibrated statement of correctness."
    )

    summary = usage_summary()
    st.markdown("**Usage on this instance**")
    st.write(
        f"{summary['sessions']} unique sessions · {summary['analyses']} analyses · "
        f"{summary['reviews']:,} reviews processed"
    )
    st.caption(
        "Local log only. It resets on Streamlit Community Cloud when the app restarts; "
        "use the webhook described in `docs/FEEDBACK.md` for durable counts."
    )

    st.markdown(f"Full evaluation: [{REPO_URL}/blob/main/reports/EVALUATION.md]({REPO_URL}/blob/main/reports/EVALUATION.md)")

with feedback_tab:
    st.markdown(
        "**This build is being tested by real users.** Bugs, confusing labels, missing features — "
        "all of it is useful. Feedback is stored with an anonymous session id, never with your review text."
    )

    form_url = feedback_form_url()
    if form_url:
        st.link_button("Prefer a Google Form? Open it here", form_url)

    with st.form("feedback_form"):
        category_label = st.selectbox("What kind of feedback is this?", list(CATEGORY_CHOICES))
        message = st.text_area(
            "What happened?",
            height=140,
            placeholder="Example: I pasted a sarcastic review and the app called it positive. "
            "The confidence was 91%, which made it more confusing.",
        )
        page = st.selectbox("Where did it happen?", PAGE_CHOICES)
        contact = st.text_input("Name or contact (optional)", placeholder="Only if you want a reply")

        submitted = st.form_submit_button("Send feedback", type="primary")

    if submitted:
        category = CATEGORY_CHOICES[category_label]
        problem = validate_feedback(message, category)
        if problem:
            st.warning(problem)
        else:
            try:
                outcome = submit_feedback(
                    category=category,
                    message=message,
                    contact=contact,
                    page=page,
                    session_id=st.session_state.session_id,
                )
            except ValueError as exc:
                st.warning(str(exc))
            else:
                st.success("Thank you — the feedback was recorded. If the owner replies, they will use the contact you left.")
                if outcome["webhook"] is False:
                    st.warning(
                        "The remote feedback endpoint did not accept the submission, so it was only saved on this server. "
                        "Copy the block below and send it to the app owner."
                    )
                if not outcome["local"] or not webhook_url():
                    st.caption(
                        "This deployment has no remote feedback backend configured, and hosted filesystems reset. "
                        "Copy this record and send it to the app owner:"
                    )
                    st.code(json.dumps(outcome["record"], indent=2, ensure_ascii=False), language="json")

st.divider()
st.caption(
    f"ReviewPulse v{APP_VERSION} · a capstone project by Gulnar Hasanova · "
    f"[source, evaluation and limitations]({REPO_URL})"
)
