import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from paper_watch.ingestion.arxiv import ArxivClient, Paper

class TestArxivClient(unittest.TestCase):
    def setUp(self):
        self.client = ArxivClient(max_results=2)

    @patch('httpx.get')
    def test_fetch_papers_success(self, mock_get):
        # Mock Arxiv API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2101.00001v1</id>
    <title>Test Paper 1</title>
    <summary>This is a test abstract 1.</summary>
    <published>2021-01-01T00:00:00Z</published>
    <link href="http://arxiv.org/abs/2101.00001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2101.00001v1" rel="related" type="application/pdf"/>
    <author><name>Author One</name></author>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="q-fin.ST" scheme="http://arxiv.org/schemas/atom"/>
    <category term="q-fin.ST" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>"""
        mock_get.return_value = mock_response

        papers = self.client.fetch_papers()

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Test Paper 1")
        self.assertEqual(papers[0].source_id, "2101.00001v1")
        self.assertEqual(papers[0].pdf_url, "http://arxiv.org/pdf/2101.00001v1")
        self.assertEqual(papers[0].authors, ["Author One"])
        self.assertEqual(papers[0].primary_category, "q-fin.ST")

    @patch('httpx.get')
    def test_fetch_papers_failure(self, mock_get):
        import httpx
        mock_get.side_effect = httpx.HTTPError("Network error")
        papers = self.client.fetch_papers()
        self.assertEqual(papers, [])

if __name__ == '__main__':
    unittest.main()
