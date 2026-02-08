import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from paper_watch.ingestion.ssrn import SSRNClient
from paper_watch.models import Paper

class TestSSRNClient(unittest.TestCase):
    def setUp(self):
        self.client = SSRNClient(journal_ids=["1508111"])

    @patch('httpx.get')
    def test_fetch_papers_success(self, mock_get):
        # Mock SSRN RSS response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version='1.0' encoding='UTF-8'?>
<rss version="2.0">
  <channel>
    <item>
      <title>Test SSRN Paper 1</title>
      <link>https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1234567</link>
      <description>This is a test SSRN abstract 1.</description>
      <pubDate>Fri, 01 Jan 2021 00:00:00 GMT</pubDate>
      <author>Author One</author>
    </item>
  </channel>
</rss>"""
        mock_get.return_value = mock_response

        papers = self.client.fetch_papers()

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Test SSRN Paper 1")
        self.assertEqual(papers[0].source_id, "1234567")
        self.assertEqual(papers[0].source, "ssrn")
        self.assertEqual(papers[0].authors, ["Author One"])

    @patch('httpx.get')
    def test_fetch_papers_403(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        papers = self.client.fetch_papers()
        self.assertEqual(papers, [])

    @patch('httpx.get')
    def test_fetch_papers_failure(self, mock_get):
        import httpx
        mock_get.side_effect = httpx.HTTPError("Network error")
        papers = self.client.fetch_papers()
        self.assertEqual(papers, [])

if __name__ == '__main__':
    unittest.main()
