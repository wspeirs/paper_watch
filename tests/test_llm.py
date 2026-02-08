import unittest
from unittest.mock import patch, MagicMock
import json
from paper_watch.intelligence.llm import GeminiClient, FilterResult

class TestGeminiClient(unittest.TestCase):
    def setUp(self):
        # Initialize with a dummy key to avoid warning
        self.client = GeminiClient(api_key="dummy_key")

    @patch('google.genai.Client')
    def test_screen_abstract_keep(self, mock_client_class):
        # Setup mock client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Re-initialize to use the mock
        self.client = GeminiClient(api_key="dummy_key")
        
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "keep": True,
            "reasoning": "This paper is about statistical arbitrage in stocks."
        })
        mock_client.models.generate_content.return_value = mock_response

        result = self.client.screen_abstract(
            "Statistical Arbitrage in Stocks",
            "This paper explores statistical arbitrage strategies for equity markets."
        )

        self.assertTrue(result.keep)
        self.assertIn("statistical arbitrage", result.reasoning.lower())

    @patch('google.genai.Client')
    def test_screen_abstract_discard(self, mock_client_class):
        # Setup mock client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        self.client = GeminiClient(api_key="dummy_key")

        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "keep": False,
            "reasoning": "This paper is about crypto bonds, which is out of scope."
        })
        mock_client.models.generate_content.return_value = mock_response

        result = self.client.screen_abstract(
            "Crypto Bonds: A New Asset Class",
            "This paper discusses the emergence of bonds backed by cryptocurrency."
        )

        self.assertFalse(result.keep)
        self.assertIn("crypto", result.reasoning.lower())

    @patch('google.genai.Client')
    def test_screen_abstract_error(self, mock_client_class):
        # Setup mock client to raise error
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        self.client = GeminiClient(api_key="dummy_key")
        
        mock_client.models.generate_content.side_effect = Exception("API error")

        result = self.client.screen_abstract("Any Title", "Any Abstract")

        self.assertFalse(result.keep)
        self.assertIn("Error", result.reasoning)

    @patch('google.genai.Client')
    def test_analyze_full_paper_success(self, mock_client_class):
        # Setup mock client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        self.client = GeminiClient(api_key="dummy_key")

        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "summary": "Core idea",
            "methodology": "Stats",
            "data": "Stocks",
            "results": "Win",
            "relevance_reconfirmed": True,
            "reasoning": "Good paper"
        })
        mock_client.models.generate_content.return_value = mock_response

        result = self.client.analyze_full_paper("Title", "Full Text")

        self.assertEqual(result.summary, "Core idea")
        self.assertTrue(result.relevance_reconfirmed)

if __name__ == '__main__':
    unittest.main()