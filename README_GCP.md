# Google Cloud Setup for Paper Watch Bot

This guide explains how to set up the Google Cloud Platform (GCP) infrastructure for the Paper Watch Bot.

## Prerequisites

1.  [Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/docs/install) installed and authenticated (`gcloud auth login`).
2.  A Google Cloud Project created (or create one via console).
3.  Billing enabled for the project.

## Automated Setup

Use the provided script to enable APIs and create the Service Account.

```bash
./scripts/setup_gcp.sh <YOUR_PROJECT_ID>
```

## Manual Configuration Steps

### 1. Secrets Management

Store sensitive keys in Google Secret Manager.

**Required Secrets:**

*   `GOOGLE_API_KEY`: API Key for Gemini (Vertex AI or AI Studio).
*   `SENDGRID_API_KEY`: API Key for SendGrid (for email delivery).

**Commands:**

```bash
# Create GOOGLE_API_KEY secret
echo -n "YOUR_GEMINI_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=- --replication-policy="automatic"

# Create SENDGRID_API_KEY secret
echo -n "YOUR_SENDGRID_KEY" | gcloud secrets create SENDGRID_API_KEY --data-file=- --replication-policy="automatic"
```

### 2. Grant Access to Secrets

Ensure the Service Account created by the script has access to these secrets. The script assigns `roles/secretmanager.secretAccessor` to the service account, which grants read access to all secrets in the project.

## Deployment

Refer to the main `README.md` or `PROJECT_PLAN.md` for deployment instructions (building the container and deploying to Cloud Run).
