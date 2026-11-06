"""Non-interactive Streamlit smoke test for the deployed app shape."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest


def button(app, label):
    for candidate in app.button:
        if candidate.label == label:
            return candidate
    raise AssertionError(f"Button not found: {label}")


def main() -> None:
    app = AppTest.from_file(ROOT / "app.py")
    app.run(timeout=60)
    assert not app.exception, app.exception
    assert app.title and "ReviewPulse" in app.title[0].value
    assert len(app.tabs) == 4

    # An example button must populate the review box.
    button(app, "Sarcastic").click()
    app.run(timeout=60)
    assert "broke after two days" in app.text_area[0].value

    app.text_area[0].input("The product arrived early and works perfectly.")
    button(app, "Analyze review").click()
    app.run(timeout=60)
    assert not app.exception, app.exception
    assert app.subheader and "Positive sentiment" in app.subheader[0].value

    # The feedback form must validate and accept a submission without crashing.
    app.selectbox[0].select("Bug — something broke or gave a wrong result")
    app.text_area[1].input("Smoke test: the batch download button returned an empty file.")
    button(app, "Send feedback").click()
    app.run(timeout=60)
    assert not app.exception, app.exception
    assert any("Thank you" in item.value for item in app.success)

    print("UI smoke test passed: onboarding, example, analysis and feedback form.")


if __name__ == "__main__":
    main()
