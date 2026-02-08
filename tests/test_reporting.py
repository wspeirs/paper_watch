import unittest
from datetime import datetime
from paper_watch.reporting.formatter import ReportFormatter
from paper_watch.models import Paper
from paper_watch.intelligence.llm import DeepAnalysisResult

class TestReportFormatter(unittest.TestCase):
    def test_format_markdown(self):
        paper = Paper(
            title="Test Paper",
            abstract="Abstract",
            pdf_url="http://pdf",
            source_id="123",
            published_date=datetime.now(),
            authors=["Author"],
            primary_category="cat",
            all_categories=["cat"],
            source="arxiv"
        )
        analysis = DeepAnalysisResult(
            summary="Summary",
            methodology="Method",
            data="Data",
            results="Results",
            relevance_score=8,
            reasoning="Reason"
        )
        
        discarded = Paper(
            title="Discarded Paper",
            abstract="Abstract",
            pdf_url="http://pdf2",
            source_id="456",
            published_date=datetime.now(),
            authors=["Author2"],
            primary_category="cat",
            all_categories=["cat"],
            source="ssrn"
        )

        report = ReportFormatter.format_markdown([(paper, analysis)], [discarded])
        
        self.assertIn("# Paper Watch Daily Digest", report)
        self.assertIn("Test Paper", report)
        self.assertIn("Discarded Paper", report)
        self.assertIn("Summary", report)

if __name__ == '__main__':
    unittest.main()
