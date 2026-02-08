import logging
import os
from typing import Optional

import fitz  # PyMuPDF
import httpx

logger = logging.getLogger(__name__)

def download_pdf(url: str, save_path: str) -> bool:
    """Downloads a PDF from a URL and saves it to the specified path."""
    try:
        logger.info(f"Downloading PDF from: {url}")
        response = httpx.get(url, timeout=30, follow_redirects=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        logger.error(f"Error downloading PDF from {url}: {e}")
        return False

def extract_text_from_pdf(pdf_path: str, max_pages: int = 20) -> Optional[str]:
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        return None
