"""Feedback capture with a pluggable backend.

Default behaviour is a local CSV append, which is enough for a laptop demo.
For a public deployment (where the filesystem is ephemeral) point
REVIEWPULSE_WEBHOOK_URL at a Google Apps Script, Formspree or any endpoint that
accepts JSON. A plain Google Form can also be linked with
REVIEWPULSE_FEEDBACK_FORM_URL.
"""
from __future__ import annotations

import os
import threading

import requests

from src.service import log_feedback

CATEGORY_CHOICES = {
    "Bug — something broke or gave a wrong result": "bug",
    "Confusion — I did not understand something": "confusion",
    "Feature request — something is missing": "feature",
    "Other — praise, question, anything else": "other",
}

PAGE_CHOICES = [
    "Try it (single review)",
    "Batch CSV",
    "Model & data",
    "Feedback form",
    "Somewhere else",
]


def _setting(name: str) -> str | None:
    """Read a setting from the environment first, then Streamlit secrets."""
    value = os.environ.get(name)
    if value:
        return value.strip()
    try:
        import streamlit as st

        secret = st.secrets.get(name)
    except Exception:
        return None
    return str(secret).strip() if secret else None


def webhook_url() -> str | None:
    return _setting("REVIEWPULSE_WEBHOOK_URL")


def feedback_form_url() -> str | None:
    return _setting("REVIEWPULSE_FEEDBACK_FORM_URL")


def validate_feedback(message: str, category: str) -> str | None:
    """Return a human-readable problem, or None when the submission is usable."""
    if category not in CATEGORY_CHOICES.values():
        return "Choose a feedback category."
    if not message or not message.strip():
        return "Write a sentence about what happened."
    if len(message) > 4000:
        return "Please keep the message under 4000 characters."
    return None


def _post(url: str, payload: dict, timeout: int = 10) -> bool:
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        return response.ok
    except requests.RequestException:
        return False


def submit_feedback(
    category: str,
    message: str,
    contact: str = "",
    page: str = "",
    session_id: str = "",
) -> dict:
    """Store feedback locally and, when configured, forward it to a webhook."""
    problem = validate_feedback(message, category)
    if problem:
        raise ValueError(problem)

    record = {
        "session_id": session_id,
        "category": category,
        "message": message.strip(),
        "contact": contact.strip(),
        "page": page,
    }
    local_saved = log_feedback(record)

    endpoint = webhook_url()
    delivered = None
    if endpoint:
        delivered = _post(endpoint, {"type": "feedback", **record})

    return {"local": local_saved, "webhook": delivered, "record": record}


def send_event(event_type: str, payload: dict) -> None:
    """Best-effort analytics ping that never blocks the UI."""
    endpoint = webhook_url()
    if not endpoint:
        return
    body = {"type": event_type, **payload}

    def worker() -> None:
        _post(endpoint, body, timeout=8)

    threading.Thread(target=worker, daemon=True).start()
