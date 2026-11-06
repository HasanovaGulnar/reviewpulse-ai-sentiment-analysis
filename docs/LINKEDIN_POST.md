# LinkedIn draft

Most sentiment demos show a label. Mine shows the probability that the label is wrong.

I built **ReviewPulse**, a small app that triages customer reviews for sellers who cannot read thousands of them. Paste one review or upload a CSV: negative / neutral / positive, with a confidence score and a per-class probability breakdown.

The interesting part was not the classifier. It was admitting where it fails:

- TF-IDF + Logistic Regression: 714 KB, about 1 ms per review on CPU.
- Test macro F1 0.664; **neutral is the weak class (0.43)**, so the UI shows all three probabilities and warns below 50% confidence.
- "Great, it broke after two days" → positive, 57.8%. That example is in the writeup, not hidden.

The case study covers the architecture, three trade-offs (classical vs transformer, committing the artifact vs training at boot, three classes vs two), and what I would fix next.

Case study: https://hasanovagulnar.github.io/reviewpulse-ai-sentiment-analysis/
Code: https://github.com/HasanovaGulnar/reviewpulse-ai-sentiment-analysis

#NLP #MachineLearning #DataScience #Python #Portfolio
