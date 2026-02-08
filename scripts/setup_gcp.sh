#!/bin/bash
set -e

# Configuration
PROJECT_ID=$1
REGION="us-central1"
SERVICE_ACCOUNT_NAME="paper-watch-bot"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    exit 1
fi

echo "Setting up Google Cloud Project: $PROJECT_ID"

# 1. Set Project
gcloud config set project "$PROJECT_ID"

# 2. Enable APIs
echo "Enabling APIs..."
gcloud services enable 
    aiplatform.googleapis.com 
    run.googleapis.com 
    cloudbuild.googleapis.com 
    firestore.googleapis.com 
    secretmanager.googleapis.com 
    cloudscheduler.googleapis.com

# 3. Create Service Account
echo "Creating Service Account..."
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" > /dev/null 2>&1; then
    echo "Service Account $SERVICE_ACCOUNT_NAME already exists."
else
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" 
        --display-name="Paper Watch Bot Service Account"
fi

SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# 4. Assign Roles
echo "Assigning Roles..."
# Vertex AI User (for Gemini)
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" 
    --role="roles/aiplatform.user"

# Firestore User (for state management)
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" 
    --role="roles/datastore.user"

# Secret Manager Accessor (for API keys)
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" 
    --role="roles/secretmanager.secretAccessor"

# Cloud Run Invoker (if needed to invoke itself, though usually Scheduler does this)
gcloud projects add-iam-policy-binding "$PROJECT_ID" 
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" 
    --role="roles/run.invoker"

echo "Setup complete!"
echo "Service Account Email: $SERVICE_ACCOUNT_EMAIL"
echo "Next steps:"
echo "1. Create secrets in Secret Manager for:"
echo "   - GOOGLE_API_KEY"
echo "   - SENDGRID_API_KEY"
echo "2. Configure Cloud Scheduler to trigger the Cloud Run Job."
