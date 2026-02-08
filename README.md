# Paper Watch
Monitor SSRN and Arxiv for new papers.

This project is largely built using Gemini.

## Local Development & Testing

You can run the full ingestion and analysis process locally. This will fetch papers, use Gemini for analysis, update your Firestore database, and send an email report.

### Prerequisites

1.  **Python & uv:** Ensure you have `uv` installed.
2.  **GCP Project:** A Google Cloud Project with Firestore initialized.
3.  **API Keys:** A `GOOGLE_API_KEY` for Gemini.

### Setup

1.  **Authenticate with GCP:**
    If you haven't already, authenticate to allow local code to access Firestore:
    ```bash
    gcloud auth application-default login
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file or export the following variables in your terminal:

    ```bash
    # GCP Config
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_API_KEY="your-gemini-api-key"

    # Email Config (Optional: If not set, email is printed to logs)
    export RECIPIENT_EMAIL="your-email@example.com"
    export SMTP_HOST="smtp.gmail.com"
    export SMTP_PORT="587"
    export SMTP_USER="your-smtp-user"
    export SMTP_PASSWORD="your-smtp-password"
    ```

### Running Locally

Run the main script using `uv`:

```bash
uv run python -m src.paper_watch.main
```

This command will:
1.  Fetch the latest papers from Arxiv.
2.  Check Firestore to see if they have already been processed.
3.  Perform abstract screening and full-paper deep analysis using Gemini.
4.  Save results to Firestore.
5.  Send a summary email to the `RECIPIENT_EMAIL`.

### Testing

To run the test suite:

```bash
uv run pytest
```


