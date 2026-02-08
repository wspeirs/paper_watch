import logging
from datetime import datetime
from typing import Optional, Any, Dict

from google.cloud import firestore

from .models import Paper
from .intelligence.llm import FilterResult, DeepAnalysisResult

logger = logging.getLogger(__name__)

class FirebaseClient:
    def __init__(self, project_id: Optional[str] = None, collection_name: str = "papers"):
        try:
            self.db = firestore.Client(project=project_id)
            self.collection = self.db.collection(collection_name)
            logger.info(f"Initialized Firestore client for collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            self.db = None

    def paper_exists(self, doc_id: str) -> bool:
        """Checks if a paper with the given ID already exists in Firestore."""
        if not self.db:
            return False
        
        try:
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking existence for {doc_id}: {e}")
            return False

    def save_paper(self, paper: Paper, filter_result: FilterResult, analysis_result: Optional[DeepAnalysisResult] = None):
        """Saves paper details and analysis results to Firestore."""
        if not self.db:
            return

        doc_id = paper.source_id
        if not doc_id:
            logger.warning(f"Paper {paper.title} has no source_id, skipping persistence.")
            return

        data: Dict[str, Any] = {
            "title": paper.title,
            "abstract": paper.abstract,
            "url": paper.pdf_url,
            "published_date": paper.published_date,
            "source": paper.source,
            "processed_at": datetime.now(),
            
            # Filter Results
            "filter_relevance_score": filter_result.relevance_score,
            "filter_reasoning": filter_result.reasoning,
        }

        if analysis_result:
            data.update({
                "deep_summary": analysis_result.summary,
                "deep_methodology": analysis_result.methodology,
                "deep_data": analysis_result.data,
                "deep_results": analysis_result.results,
                "deep_relevance_score": analysis_result.relevance_score,
                "deep_reasoning": analysis_result.reasoning,
            })

        try:
            self.collection.document(doc_id).set(data)
            logger.info(f"Saved paper {doc_id} to Firestore.")
        except Exception as e:
            logger.error(f"Error saving paper {doc_id} to Firestore: {e}")
