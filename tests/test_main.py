import unittest
from unittest.mock import patch, MagicMock
from src.paper_watch.main import main

class TestMain(unittest.TestCase):
    @patch('src.paper_watch.main.ArxivClient')
    @patch('src.paper_watch.main.GeminiClient')
    @patch('src.paper_watch.main.EmailClient')
    @patch('src.paper_watch.main.FirebaseClient')
    @patch('src.paper_watch.main.download_pdf')
    @patch('src.paper_watch.main.extract_text_from_pdf')
    def test_main_flow(self, mock_extract, mock_download, mock_firebase, mock_email, mock_gemini, mock_arxiv):
        # Setup mocks
        mock_arxiv_inst = mock_arxiv.return_value
        mock_arxiv_inst.fetch_papers.return_value = [
            MagicMock(title="Paper 1", abstract="Abstract 1", pdf_url="http://pdf1", source="arxiv", source_id="1", authors=["A1"])
        ]
        
        mock_firebase_inst = mock_firebase.return_value
        mock_firebase_inst.paper_exists.return_value = False
        
        mock_gemini_inst = mock_gemini.return_value
        mock_gemini_inst.screen_abstract.return_value = MagicMock(relevance_score=5, reasoning="Keep it")
        mock_gemini_inst.analyze_full_paper.return_value = MagicMock(
            summary="Sum", methodology="Meth", data="Data", results="Res", 
            relevance_score=9, reasoning="Still good"
        )
        
        mock_download.return_value = True
        mock_extract.return_value = "Full text content"
        
        # Run main
        main()
        
        # Verify calls
        mock_arxiv_inst.fetch_papers.assert_called_once()
        mock_gemini_inst.screen_abstract.assert_called_once()
        mock_gemini_inst.analyze_full_paper.assert_called_once()
        mock_email.return_value.send_email.assert_called_once()
        mock_firebase_inst.save_paper.assert_called_once()

if __name__ == '__main__':
    unittest.main()
