import unittest
from app import get_stock_data, analyze_sentiment

class TestApp(unittest.TestCase):
    def test_get_stock_data(self):
        data = get_stock_data("AAPL")
        self.assertIsNotNone(data)
        self.assertIn("Close", data.columns)

    def test_analyze_sentiment(self):
        articles = ["Great news!", "Terrible outcome.", "Neutral statement."]
        sentiments = analyze_sentiment(articles)
        self.assertEqual(sentiments, ["Positive", "Negative", "Neutral"])

if __name__ == "__main__":
    unittest.main()