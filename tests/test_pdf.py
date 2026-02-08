import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
from paper_watch.utils.pdf import download_pdf, extract_text_from_pdf

class TestPDFUtils(unittest.TestCase):

    @patch('httpx.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_pdf_success(self, mock_file, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"%PDF-1.4 test content"
        mock_get.return_value = mock_response

        result = download_pdf("http://example.com/test.pdf", "test.pdf")

        self.assertTrue(result)
        mock_get.assert_called_once_with("http://example.com/test.pdf", timeout=30, follow_redirects=True)
        mock_file().write.assert_called_once_with(b"%PDF-1.4 test content")

    @patch('httpx.get')
    def test_download_pdf_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        result = download_pdf("http://example.com/test.pdf", "test.pdf")
        self.assertFalse(result)

    @patch('fitz.open')
    def test_extract_text_from_pdf_success(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Extracted Text"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        text = extract_text_from_pdf("test.pdf")

        self.assertEqual(text, "Extracted Text")
        mock_doc.close.assert_called_once()

    @patch('fitz.open')
    def test_extract_text_from_pdf_failure(self, mock_fitz_open):
        mock_fitz_open.side_effect = Exception("File error")
        text = extract_text_from_pdf("test.pdf")
        self.assertIsNone(text)

if __name__ == '__main__':
    unittest.main()
