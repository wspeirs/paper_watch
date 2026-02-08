import logging
import os
import tempfile
from datetime import datetime, timedelta

from dotenv import load_dotenv

from .ingestion import ArxivClient #, SSRNClient
from .intelligence import GeminiClient
from .reporting import ReportFormatter, EmailClient
from .utils import download_pdf, extract_text_from_pdf
from .firebase import FirebaseClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KEEP_THRESHOLD = 3
DEEP_ANALYSIS_THRESHOLD = 6

def main():
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # DEBUG: Check if env vars are loaded
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        logger.info(f"DEBUG: GOOGLE_API_KEY loaded: {api_key[:5]}...{api_key[-5:]}")
    else:
        logger.error("DEBUG: GOOGLE_API_KEY is NOT set")

    recipient = os.environ.get("RECIPIENT_EMAIL")

    if recipient is None:
        raise ValueError("No recipient specified")
    
    # 1. Initialize clients
    arxiv_client = ArxivClient(max_results=10)
    # ssrn_client = SSRNClient()
    gemini_client = GeminiClient()
    email_client = EmailClient()
    firebase_client = FirebaseClient()
    
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
        if firebase_client.paper_exists(paper.source_id):
            logger.info(f"Paper {paper.source_id} already processed. Skipping.")
            continue

        logger.info(f"Screening abstract: {paper.title}")
        filter_result = gemini_client.screen_abstract(paper.title, paper.abstract)
        
        analysis = None

        if filter_result.relevance_score >= KEEP_THRESHOLD:
            logger.info(f"Paper kept (Score: {filter_result.relevance_score}): {paper.title}. Reasoning: {filter_result.reasoning}")
            
            # Download and Deep Analyze
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                if download_pdf(paper.pdf_url, tmp_path):
                    text = extract_text_from_pdf(tmp_path)
                    if text:
                        analysis = gemini_client.analyze_full_paper(paper.title, text)
                        if analysis.relevance_score >= DEEP_ANALYSIS_THRESHOLD:
                            logger.info(f"Relevance reconfirmed (Score: {analysis.relevance_score}) for: {paper.title}")
                            relevant_papers_with_analysis.append((paper, analysis))
                        else:
                            logger.info(f"Paper re-classified as not relevant (Score: {analysis.relevance_score}): {paper.title}. Reasoning: {analysis.reasoning}")
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
            logger.info(f"Paper discarded (Score: {filter_result.relevance_score}): {paper.title}. Reasoning: {filter_result.reasoning}")
            discarded_papers.append(paper)
        
        # Save to Firebase
        firebase_client.save_paper(paper, filter_result, analysis)

    # 4. Generate Report
    logger.info("Generating reports...")
    report_md = ReportFormatter.format_markdown(relevant_papers_with_analysis, discarded_papers)
    report_html = ReportFormatter.format_html(relevant_papers_with_analysis, discarded_papers)
    
    # 5. Send Email
    subject = f"Paper Watch Digest - {datetime.now().strftime('%Y-%m-%d')}"
    
    logger.info(f"Sending email to {recipient}...")
    email_client.send_email(recipient, subject, report_md, report_html)
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
