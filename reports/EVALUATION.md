# ReviewPulse model evaluation

Training ran on **2026-11-03** using the saved deterministic Yelp sample.

| Split | Rows | Macro F1 |
|---|---:|---:|
| Validation | 300 | 0.584 |
| Test | 300 | 0.664 |

Held-out test metrics:

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Negative | 0.793 | 0.793 | 0.793 | 116 |
| Neutral | 0.441 | 0.413 | 0.426 | 63 |
| Positive | 0.760 | 0.785 | 0.772 | 121 |

The model distinguishes clearly positive and clearly negative reviews much
better than neutral reviews. This is expected because neutral is a narrower
class after mapping Yelp's five-star scale to three classes. ReviewPulse should
be used as a triage tool, not as an automated customer-service decision-maker.

The full reproducible metrics, class distributions and confusion matrices are
stored in [metrics.json](metrics.json).
