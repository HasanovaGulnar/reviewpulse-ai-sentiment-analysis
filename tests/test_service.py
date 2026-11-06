import unittest

from src.service import predict_reviews, read_usage_summary


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

    def test_prediction_output_has_class_probabilities(self):
        result = predict_reviews(FakeModel(), ["Very good service"])
        self.assertAlmostEqual(result.loc[0, "p_negative"], 0.1)
        self.assertAlmostEqual(result.loc[0, "p_neutral"], 0.2)
        self.assertAlmostEqual(result.loc[0, "p_positive"], 0.7)

    def test_empty_review_rejected(self):
        with self.assertRaises(ValueError):
            predict_reviews(FakeModel(), ["  "])

    def test_usage_summary_counts_unique_sessions(self):
        import tempfile
        from pathlib import Path

        rows = (
            "timestamp_utc,session_id,action,review_count,app_version\n"
            "2026-01-01T00:00:00Z,a,session_start,0,1.1.0\n"
            "2026-01-01T00:00:01Z,a,single_review,1,1.1.0\n"
            "2026-01-01T00:00:02Z,b,session_start,0,1.1.0\n"
            "2026-01-01T00:00:03Z,b,batch_csv,4,1.1.0\n"
            "2026-01-01T00:00:04Z,aa,session_start,0,1.1.0\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "usage.csv"
            path.write_text(rows, encoding="utf-8")
            summary = read_usage_summary(path)
        self.assertEqual(summary["sessions"], 3)
        self.assertEqual(summary["analyses"], 2)
        self.assertEqual(summary["reviews"], 5)

    def test_missing_usage_log_is_not_an_error(self):
        summary = read_usage_summary(__import__("pathlib").Path("does-not-exist.csv"))
        self.assertEqual(summary["sessions"], 0)
        self.assertFalse(summary["available"])


if __name__ == "__main__":
    unittest.main()
