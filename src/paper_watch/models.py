from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Paper:
    title: str
    abstract: str
    pdf_url: str
    source_id: str  # arxiv_id or ssrn_id
    published_date: datetime
    authors: List[str]
    primary_category: str
    all_categories: List[str]
    source: str  # "arxiv" or "ssrn"
