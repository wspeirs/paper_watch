# Project Context

*   **Language:** Python
*   **Dependency Manager:** `uv` (use `uv run pytest` for tests)
*   **Libraries:** `httpx` (preferred over `requests`)
*   **Goal:** Paper Watch Bot (Arxiv) for Quantitative Finance/Statistics.
*   **Status:** SSRN ingestion is currently disabled due to site instability/Cloudflare.
*   **User Email:** `bill.speirs@gmail.com`
*   **Environment:** Running in a sandbox; full access to all tools.
*   **Filtering Logic:**
    *   **Keep:** Statistical arbitrage, stocks, options, time-series data.
    *   **Discard:** Bonds, crypto, other asset classes.
*   **Workflow:**
    1.  Fetch papers (Arxiv).
    2.  Gemini Filter on Abstract.
    3.  If relevant -> Download PDF -> Gemini Analysis.
    4.  Generate Summaries & Discard List.
    5.  Email Report.
