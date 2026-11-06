import unittest

from src.feedback import CATEGORY_CHOICES, validate_feedback


class FeedbackValidationTests(unittest.TestCase):
    def test_valid_bug_feedback(self):
        self.assertIsNone(validate_feedback("The CSV download was empty.", "bug"))

    def test_empty_message_rejected(self):
        self.assertIsNotNone(validate_feedback("   ", "bug"))

    def test_unknown_category_rejected(self):
        self.assertIsNotNone(validate_feedback("Something happened.", "nonsense"))

    def test_long_message_rejected(self):
        self.assertIsNotNone(validate_feedback("x" * 4001, "confusion"))

    def test_categories_cover_the_required_buckets(self):
        self.assertEqual(set(CATEGORY_CHOICES.values()), {"bug", "confusion", "feature", "other"})


if __name__ == "__main__":
    unittest.main()
