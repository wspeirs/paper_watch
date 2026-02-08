#!/bin/bash
set -e

# Configuration
PROJECT_ID=$1
REGION="us-central1"
JOB_NAME="paper-watch-bot"
IMAGE_NAME="gcr.io/$PROJECT_ID/$JOB_NAME"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    exit 1
fi

echo "Deploying $JOB_NAME to $PROJECT_ID in $REGION"

# 1. Build and push image using Cloud Build
echo "Building and pushing image..."
gcloud builds submit --tag "$IMAGE_NAME" .

# 2. Create or Update Cloud Run Job
echo "Creating/Updating Cloud Run Job..."
if gcloud run jobs describe "$JOB_NAME" --region "$REGION" > /dev/null 2>&1; then
    gcloud run jobs update "$JOB_NAME" 
        --image "$IMAGE_NAME" 
        --region "$REGION" 
        --service-account "paper-watch-bot@$PROJECT_ID.iam.gserviceaccount.com"
else
    gcloud run jobs create "$JOB_NAME" 
        --image "$IMAGE_NAME" 
        --region "$REGION" 
        --service-account "paper-watch-bot@$PROJECT_ID.iam.gserviceaccount.com"
fi

# 3. Configure Cloud Scheduler
echo "Configuring Cloud Scheduler..."
if gcloud scheduler jobs describe "${JOB_NAME}-trigger" --location "$REGION" > /dev/null 2>&1; then
    gcloud scheduler jobs update http "${JOB_NAME}-trigger" 
        --location "$REGION" 
        --schedule="0 6 * * *" 
        --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" 
        --http-method=POST 
        --oauth-service-account-email="paper-watch-bot@$PROJECT_ID.iam.gserviceaccount.com"
else
    gcloud scheduler jobs create http "${JOB_NAME}-trigger" 
        --location "$REGION" 
        --schedule="0 6 * * *" 
        --uri="https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" 
        --http-method=POST 
        --oauth-service-account-email="paper-watch-bot@$PROJECT_ID.iam.gserviceaccount.com"
fi

echo "Deployment complete!"
