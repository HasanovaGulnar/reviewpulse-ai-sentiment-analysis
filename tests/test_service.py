import unittest

from src.service import predict_reviews


class FakeClassifier:
    classes_ = [0, 1, 2]


class FakeModel:
    named_steps = {"classifier": FakeClassifier()}

    def predict_proba(self, texts):
        return [[0.1, 0.2, 0.7] for _ in texts]


class ServiceTests(unittest.TestCase):
    def test_prediction_output_has_sentiment_and_confidence(self):
        result = predict_reviews(FakeModel(), ["Very good service"])
        self.assertEqual(result.loc[0, "sentiment"], "positive")
        self.assertAlmostEqual(result.loc[0, "confidence"], 0.7)

    def test_empty_review_rejected(self):
        with self.assertRaises(ValueError):
            predict_reviews(FakeModel(), ["  "])
