import json
import logging
import os
from typing import Optional, Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class FilterResult(BaseModel):
    keep: bool
    reasoning: str

class DeepAnalysisResult(BaseModel):
    summary: str
    methodology: str
    data: str
    results: str
    relevance_reconfirmed: bool
    reasoning: str

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment or passed to constructor.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def screen_abstract(self, title: str, abstract: str) -> FilterResult:
        # ... (implementation remains same)
        prompt = f"""
You are an expert quantitative finance researcher. Your task is to screen academic paper abstracts for relevance to a specific trading and research focus.

Focus Areas:
- Keep: Statistical arbitrage, stocks, equities, options, derivatives, time-series analysis, medium or low frequency trading.
- Discard: Fixed income, bonds, cryptocurrency, macroeconomics (unless directly related to equity pricing), non-financial topics.

Paper Title: {title}
Abstract: {abstract}

Decide if this paper should be kept for further analysis.
Return your response in JSON format with two fields: "keep" (boolean) and "reasoning" (string).
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            # Depending on the version, response.text or response.parsed might be used.
            # For JSON mode, response.text should be the JSON string.
            data = json.loads(response.text)
            return FilterResult(**data)
        except Exception as e:
            logger.error(f"Error screening abstract with Gemini: {e}")
            return FilterResult(keep=False, reasoning=f"Error during screening: {str(e)}")

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

Return your response in JSON format with these fields:
"summary", "methodology", "data", "results", "relevance_reconfirmed" (boolean), "reasoning" (explanation for relevance)
"""
        try:
            # We might need to truncate the text if it's too long for the model
            # but Gemini 1.5 Pro/Flash has a large context window.
            # For safety, let's just send the text and handle potential errors.
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            data = json.loads(response.text)
            return DeepAnalysisResult(**data)
        except Exception as e:
            logger.error(f"Error analyzing full paper with Gemini: {e}")
            return DeepAnalysisResult(
                summary="Error during analysis",
                methodology="",
                data="",
                results="",
                relevance_reconfirmed=False,
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
