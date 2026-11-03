"""Non-interactive Streamlit smoke test for the ReviewPulse demo."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest


def main() -> None:
    app = AppTest.from_file(ROOT / "app.py")
    app.run(timeout=30)
    assert not app.exception, app.exception
    assert app.title and "ReviewPulse" in app.title[0].value
    assert len(app.tabs) == 3

    app.text_area[0].input("The product arrived early and works perfectly.")
    app.button[0].click()
    app.run(timeout=30)
    assert not app.exception, app.exception
    assert app.subheader and "Positive sentiment" in app.subheader[0].value
    print("UI smoke test passed: single-review analysis returned Positive.")


if __name__ == "__main__":
    main()
