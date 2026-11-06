# Before / after: fixes shipped from real use

One entry per accepted feedback item. Keep the "before" concrete (what the user
saw), the "after" verifiable (what changed and how it was checked), and link the
commit.

---

## Fix 1 — Low-confidence results looked certain

**Source:** pre-launch QA, not an external tester. Recorded here as the baseline
for the format; the tester-driven entry is Fix 2.

**Feedback (QA note):** "I pasted a sarcastic review, the app said positive with
91% confidence and gave me nothing else to judge. On a 3-star review it said
neutral at 34% and still looked like a verdict."

**Category:** confusion / trust
**Severity:** S2 — the label is wrong in a way the UI hides
**Status:** fixed

### Before

- The single-review result showed one label and one number: `Neutral · 34%`.
- There was no warning for low confidence, no per-class breakdown, and no
  statement that `neutral` is the weakest class.
- A tester could not tell the difference between "the model is sure" and "the
  model guessed".

### After

- The result shows all three class probabilities as a bar chart next to the
  label, so the runner-up class is visible.
- Confidence below 50% renders a warning: *"Low confidence — the model is
  unsure about this one. Treat the label as a hint, not a verdict."*
- A caption next to every result states the neutral-class F1 (0.43) and that
  negation and sarcasm often flip the prediction.
- The **Model & data** tab repeats the limitation list, with the confusion
  matrix one click away.

### Verification

- `scripts/ui_smoke.py` exercises the example → analyze → result path.
- Manual check: the sarcastic example returns the probability breakdown, and a
  low-confidence input shows the warning.
- Unit tests cover the probability columns (`tests/test_service.py`).

**Commit:** see the commit that adds `p_negative` / `p_neutral` / `p_positive`
to `src/service.py` and the result block in `app.py`.

---

## Fix 2 — Pending: first issue reported by an external tester

**Source:** tester `T-__` on `____-__-__`
**Category:** bug / confusion / feature request
**Severity:** S1 / S2 / S3 / S4
**Status:** open

### Feedback (verbatim)

> _paste the tester's words here_

### Before

_What the tester saw. Include the URL, page, input and the exact output._

### After

_What changed. Keep it to the smallest change that addresses the report._

### Verification

- _Reproduction steps that now pass_
- _Test or manual check added_
- _Tester re-checked? yes / no_

**Commit:** `_______`

---

## Template for the next entry

```markdown
## Fix N — <short title>

**Source:** tester T-__ on YYYY-MM-DD
**Category:** bug / confusion / feature request
**Severity:** S1–S4
**Status:** fixed

### Feedback (verbatim)
> ...

### Before
...

### After
...

### Verification
- ...

**Commit:** `<sha>`
```
