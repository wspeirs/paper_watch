# Infrastructure Decisions

## 1. Email Service
**Decision:** **SendGrid (Free Tier)** via API.

**Reasoning:**
*   **GCP Constraints:** Google Cloud Platform (GCP) blocks standard SMTP traffic (port 25) to prevent abuse. While ports 587/465 can sometimes be used, they are not recommended for reliability.
*   **Integration:** SendGrid is well-integrated with GCP (available via Marketplace) and offers a robust HTTP API that works reliably from Cloud Run.
*   **Alternatives Considered:**
    *   *Gmail API:* Requires OAuth2 token management (refresh tokens), which adds complexity for a headless background service compared to a simple API key.
    *   *Gmail SMTP:* Likely to be blocked or require "Less Secure App" workarounds which are being deprecated.

## 2. Compute Environment
**Decision:** **Google Cloud Run Jobs**.

**Reasoning:**
*   **Fit for Purpose:** The application is a batch process (Start -> Fetch -> Process -> Email -> Stop), not a continuously running web service. Cloud Run Jobs is designed exactly for this.
*   **Cost:** "Scale to zero" means we only pay for the seconds the job is running.
*   **Scheduling:** Easily triggered by Google Cloud Scheduler (Cron).

## 3. Storage (State Management)
**Decision:** **Google Cloud Firestore**.

**Reasoning:**
*   **Requirement:** We need to track which papers (Arxiv IDs, SSRN IDs) have already been processed to prevent sending duplicate emails or missing papers if a run fails and is retried.
*   **Why Firestore:**
    *   **Serverless:** No database to provision or manage.
    *   **Cost:** The "Spark" (Free) tier is more than sufficient for storing a few hundred/thousand document IDs.
    *   **Access:** Native Python client (`google-cloud-firestore`) is simple to use.
*   **Alternatives Considered:**
    *   *SQLite:* Not viable because Cloud Run has an ephemeral file system. Data would be lost between runs.
    *   *Time-based logic only:* Risky. If the job fails one day and runs the next, strict time windows might miss papers or duplicate them. ID-tracking is more robust.
