import logging
import os
import tempfile
from datetime import datetime, timedelta

from .ingestion import ArxivClient #, SSRNClient
from .intelligence import GeminiClient
from .reporting import ReportFormatter, EmailClient
from .utils import download_pdf, extract_text_from_pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 1. Initialize clients
    arxiv_client = ArxivClient(max_results=10)
    # ssrn_client = SSRNClient()
    gemini_client = GeminiClient()
    email_client = EmailClient()
    
    # 2. Fetch papers
    logger.info("Fetching papers from Arxiv...")
    arxiv_papers = arxiv_client.fetch_papers()
    
    # logger.info("Fetching papers from SSRN...")
    # ssrn_papers = ssrn_client.fetch_papers()
    
    all_papers = arxiv_papers # + ssrn_papers
    logger.info(f"Total papers fetched: {len(all_papers)}")
    
    relevant_papers_with_analysis = []
    discarded_papers = []
    
    # 3. Filter and Analyze
    for paper in all_papers:
        logger.info(f"Screening abstract: {paper.title}")
        filter_result = gemini_client.screen_abstract(paper.title, paper.abstract)
        
        if filter_result.keep:
            logger.info(f"Paper kept: {paper.title}. Reasoning: {filter_result.reasoning}")
            
            # Download and Deep Analyze
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                if download_pdf(paper.pdf_url, tmp_path):
                    text = extract_text_from_pdf(tmp_path)
                    if text:
                        analysis = gemini_client.analyze_full_paper(paper.title, text)
                        if analysis.relevance_reconfirmed:
                            logger.info(f"Relevance reconfirmed for: {paper.title}")
                            relevant_papers_with_analysis.append((paper, analysis))
                        else:
                            logger.info(f"Paper re-classified as not relevant: {paper.title}. Reasoning: {analysis.reasoning}")
                            discarded_papers.append(paper)
                    else:
                        logger.warning(f"Could not extract text from PDF: {paper.title}")
                        discarded_papers.append(paper)
                else:
                    logger.warning(f"Could not download PDF: {paper.title}")
                    # If we can't download PDF, we might still want to include it based on abstract?
                    # For now, let's just discard it as we can't do deep analysis.
                    discarded_papers.append(paper)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            logger.info(f"Paper discarded: {paper.title}. Reasoning: {filter_result.reasoning}")
            discarded_papers.append(paper)

    # 4. Generate Report
    logger.info("Generating reports...")
    report_md = ReportFormatter.format_markdown(relevant_papers_with_analysis, discarded_papers)
    report_html = ReportFormatter.format_html(relevant_papers_with_analysis, discarded_papers)
    
    # 5. Send Email
    recipient = os.environ.get("RECIPIENT_EMAIL", "bill.speirs@gmail.com")
    subject = f"Paper Watch Digest - {datetime.now().strftime('%Y-%m-%d')}"
    
    logger.info(f"Sending email to {recipient}...")
    email_client.send_email(recipient, subject, report_md, report_html)
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
