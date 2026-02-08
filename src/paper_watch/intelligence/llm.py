import json
import logging
import os
from typing import Optional, Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class FilterResult(BaseModel):
    relevance_score: int = Field(ge=1, le=5)
    reasoning: str

class DeepAnalysisResult(BaseModel):
    summary: str
    methodology: str
    data: str
    results: str
    relevance_score: int = Field(ge=1, le=10)
    reasoning: str

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3-flash-preview"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment or passed to constructor.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def screen_abstract(self, title: str, abstract: str) -> FilterResult:
        prompt = f"""
You are an expert quantitative finance researcher. Your task is to screen academic paper abstracts for relevance to a specific trading and research focus.

Focus Areas:
- High Relevance: Statistical arbitrage, stocks, equities, options, derivatives, time-series analysis, medium or low frequency trading.
- Low Relevance: Fixed income, bonds, cryptocurrency, macroeconomics (unless directly related to equity pricing), non-financial topics.

Paper Title: {title}
Abstract: {abstract}

Assign a relevance score from 1 to 5:
5: Highly relevant, fits core focus perfectly.
4: Likely relevant, strongly related to core focus.
3: Potentially relevant, contains some interesting elements for our focus.
2: Unlikely relevant, only tangentially related.
1: Not relevant, focuses on discarded topics.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FilterResult,
                )
            )
            return response.parsed
        except Exception as e:
            logger.error(f"Error screening abstract with Gemini: {e}")
            return FilterResult(relevance_score=1, reasoning=f"Error during screening: {str(e)}")

    def analyze_full_paper(self, title: str, text: str) -> DeepAnalysisResult:
        prompt = f"""
You are an expert quantitative finance researcher. You have been provided with the full text of an academic paper titled "{title}".

Your task is to provide a detailed analysis of this paper, specifically for a team focused on statistical arbitrage, equity trading, and time-series analysis.

Analyze the paper and provide:
1. A concise summary of the core idea.
2. Details on the methodology used (e.g., specific models, statistical techniques).
3. Information about the data used (e.g., asset classes, time period, frequency).
4. Key results and findings.
5. Re-confirm if this paper is actually relevant to the focus areas (Statistical arbitrage, stocks, equities, options, derivatives, time-series analysis).

Assign a final relevance score from 1 to 10:
10: Absolutely essential reading, perfect fit.
1: Not relevant at all upon closer inspection.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DeepAnalysisResult,
                )
            )
            return response.parsed
        except Exception as e:
            logger.error(f"Error analyzing full paper with Gemini: {e}")
            return DeepAnalysisResult(
                summary="Error during analysis",
                methodology="",
                data="",
                results="",
                relevance_score=1,
                reasoning=str(e)
            )

if __name__ == "__main__":
    # Basic test (will fail without API key)
    logging.basicConfig(level=logging.INFO)
    client = GeminiClient()
    result = client.screen_abstract(
        "Statistical Arbitrage in High-Frequency Trading",
        "This paper explores various statistical arbitrage strategies using high-frequency data from the equity markets."
    )
    print(result)
