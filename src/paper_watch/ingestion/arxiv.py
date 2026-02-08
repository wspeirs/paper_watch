import logging
import time
from datetime import datetime
from typing import List, Optional

import feedparser
import httpx

from ..models import Paper

logger = logging.getLogger(__name__)

class ArxivClient:
    BASE_URL = "https://export.arxiv.org/api/query?"

    def __init__(self, categories: List[str] = ["q-fin.*"], max_results: int = 50):
        self.categories = categories
        self.max_results = max_results

    def _build_query(self) -> str:
        cat_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        query = f"search_query=({cat_query})&sortBy=submittedDate&sortOrder=descending&max_results={self.max_results}"
        return self.BASE_URL + query

    def fetch_papers(self) -> List[Paper]:
        url = self._build_query()
        logger.info(f"Fetching papers from: {url}")
        
        try:
            response = httpx.get(url, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching from Arxiv: {e}")
            return []

        feed = feedparser.parse(response.text)
        papers = []

        for entry in feed.entries:
            # Extract PDF link
            pdf_url = ""
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if link.get("type") == "application/pdf":
                        pdf_url = link.get("href", "")
                        break
            
            # If no PDF link found in links, try to construct it from id
            if not pdf_url and hasattr(entry, 'id') and "abs" in entry.id:
                 pdf_url = entry.id.replace("abs", "pdf")
            
            # Arxiv ID is usually at the end of the id link
            arxiv_id = entry.id.split("/abs/")[-1] if hasattr(entry, 'id') else ""

            # Parse published date
            # feedparser handles various date formats
            published_date = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])

            paper = Paper(
                title=entry.title.replace("\n", " ").strip() if hasattr(entry, 'title') else "",
                abstract=entry.summary.replace("\n", " ").strip() if hasattr(entry, 'summary') else "",
                pdf_url=pdf_url,
                source_id=arxiv_id,
                published_date=published_date,
                authors=[author.name for author in entry.authors] if hasattr(entry, 'authors') else [],
                primary_category=entry.arxiv_primary_category["term"] if hasattr(entry, 'arxiv_primary_category') else "",
                all_categories=[cat["term"] for cat in entry.tags] if hasattr(entry, 'tags') else [],
                source="arxiv"
            )
            papers.append(paper)

        return papers

if __name__ == "__main__":
    # Basic test
    logging.basicConfig(level=logging.INFO)
    client = ArxivClient(max_results=5)
    latest_papers = client.fetch_papers()
    for p in latest_papers:
        print(f"[{p.published_date.date()}] {p.title} ({p.source_id})")
        print(f"Authors: {', '.join(p.authors)}")
        print(f"PDF: {p.pdf_url}")
        print("-" * 40)