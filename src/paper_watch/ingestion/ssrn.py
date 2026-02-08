import logging
from datetime import datetime
from typing import List

import feedparser
import httpx
from bs4 import BeautifulSoup

from ..models import Paper

logger = logging.getLogger(__name__)

class SSRNClient:
    """
    Client for fetching papers from SSRN.
    Note: SSRN frequently uses Cloudflare, which may block direct HTTP calls.
    """
    RSS_BASE_URL = "https://papers.ssrn.com/sol3/JELJOUR_Results.cfm?n_menu=journal&form_name=journalBrowse&journal_id={journal_id}&rss=1"

    def __init__(self, journal_ids: List[str] = ["1508111"]):
        self.journal_ids = journal_ids
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_papers(self) -> List[Paper]:
        all_papers = []
        for jid in self.journal_ids:
            url = self.RSS_BASE_URL.format(journal_id=jid)
            logger.info(f"Attempting to fetch SSRN papers for journal {jid} from: {url}")
            
            try:
                response = httpx.get(
                    url, headers=self.headers, timeout=15, follow_redirects=True
                )
                if response.status_code == 403:
                    logger.error(f"Access to SSRN journal {jid} blocked by Cloudflare (403).")
                    continue
                response.raise_for_status()
                
                papers = self._parse_rss(response.text)
                all_papers.extend(papers)
                
            except httpx.HTTPError as e:
                logger.error(f"Error fetching from SSRN journal {jid}: {e}")
                
        return all_papers

    def _parse_rss(self, rss_content: str) -> List[Paper]:
        feed = feedparser.parse(rss_content)
        papers = []

        for entry in feed.entries:
            # SSRN RSS entries typically have:
            # title, link, description (abstract), dc:creator (authors), pubDate
            
            # Extract SSRN ID from link
            # e.g., https://papers.ssrn.com/sol3/papers.cfm?abstract_id=XXXXXXX
            ssrn_id = entry.link.split("abstract_id=")[-1] if hasattr(entry, 'link') else ""
            
            # Parse published date
            published_date = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])

            # Authors are often in 'authors' or 'author' or 'dc_creator'
            authors = []
            if hasattr(entry, 'author'):
                authors = [entry.author]
            elif hasattr(entry, 'authors'):
                authors = [a.name for a in entry.authors]

            paper = Paper(
                title=entry.title.replace("\n", " ").strip() if hasattr(entry, 'title') else "",
                abstract=entry.description.replace("\n", " ").strip() if hasattr(entry, 'description') else "",
                pdf_url=f"https://papers.ssrn.com/sol3/Delivery.cfm?abstract_id={ssrn_id}",
                source_id=ssrn_id,
                published_date=published_date,
                authors=authors,
                primary_category="SSRN",
                all_categories=["SSRN"],
                source="ssrn"
            )
            papers.append(paper)

        return papers

if __name__ == "__main__":
    # Basic test
    logging.basicConfig(level=logging.INFO)
    client = SSRNClient()
    latest_papers = client.fetch_papers()
    print(f"Fetched {len(latest_papers)} papers.")
    for p in latest_papers:
        print(f"[{p.published_date.date()}] {p.title} ({p.source_id})")
        print("-" * 40)
