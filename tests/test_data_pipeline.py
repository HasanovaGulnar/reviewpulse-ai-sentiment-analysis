import unittest

from src.data_pipeline import star_to_sentiment


class SentimentMappingTests(unittest.TestCase):
    def test_star_mapping(self):
        self.assertEqual(star_to_sentiment(0), "negative")
        self.assertEqual(star_to_sentiment(1), "negative")
        self.assertEqual(star_to_sentiment(2), "neutral")
        self.assertEqual(star_to_sentiment(3), "positive")
        self.assertEqual(star_to_sentiment(4), "positive")

    def test_invalid_star_mapping_rejected(self):
        with self.assertRaises(ValueError):
            star_to_sentiment(5)
