# Google Cloud Platform Deployment Guide

This document provides step-by-step instructions for deploying the Audience Deployment Automation System to Google Cloud Platform (GCP).

## Prerequisites

1. A Google Cloud Platform account with billing enabled
2. Google Cloud SDK installed and configured on your local machine
3. Required permissions to create and manage:
   - Cloud Functions
   - Cloud Storage buckets
   - IAM roles and permissions
   - Logging

## Step 1: Set Up Google Cloud Storage

1. Create a new bucket to store audience data:

```bash
gsutil mb -l [LOCATION] gs://[BUCKET_NAME]
```

Replace `[LOCATION]` with your preferred region (e.g., `us-central1`) and `[BUCKET_NAME]` with your desired bucket name.

2. Create a folder structure in the bucket:

```bash
gsutil mkdir gs://[BUCKET_NAME]/audiences
```

## Step 2: Configure Environment Variables

1. Create a `.env` file based on the `.env.example` template:

```bash
cp .env.example .env
```

2. Fill in all required API keys and credentials in the `.env` file.

3. Upload the `.env` file to Google Secret Manager:

```bash
gcloud secrets create audience-deployment-env --data-file=.env
```

## Step 3: Deploy the Cloud Function

### Option 1: Deploy with HTTP Trigger

```bash
gcloud functions deploy audience-deployment \
  --runtime python39 \
  --trigger-http \
  --entry-point process_audience \
  --memory 512MB \
  --timeout 300s \
  --set-secrets 'ENV_FILE=audience-deployment-env:latest' \
  --service-account [SERVICE_ACCOUNT_EMAIL]
```

### Option 2: Deploy with GCS Trigger

```bash
gcloud functions deploy audience-deployment-gcs \
  --runtime python39 \
  --trigger-event google.storage.object.finalize \
  --trigger-resource [BUCKET_NAME] \
  --entry-point process_gcs_trigger \
  --memory 512MB \
  --timeout 300s \
  --set-secrets 'ENV_FILE=audience-deployment-env:latest' \
  --service-account [SERVICE_ACCOUNT_EMAIL]
```

Replace `[SERVICE_ACCOUNT_EMAIL]` with your service account email and `[BUCKET_NAME]` with your GCS bucket name.

## Step 4: Set Up IAM Permissions

Ensure your Cloud Function's service account has the following permissions:

- `roles/storage.objectViewer` on the GCS bucket
- `roles/secretmanager.secretAccessor` on the Secret Manager secret
- `roles/logging.logWriter` for logging

```bash
gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member serviceAccount:[SERVICE_ACCOUNT_EMAIL] \
  --role roles/storage.objectViewer

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member serviceAccount:[SERVICE_ACCOUNT_EMAIL] \
  --role roles/secretmanager.secretAccessor

gcloud projects add-iam-policy-binding [PROJECT_ID] \
  --member serviceAccount:[SERVICE_ACCOUNT_EMAIL] \
  --role roles/logging.logWriter
```

## Step 5: Testing the Deployment

### Testing HTTP Trigger

```bash
curl -X POST [FUNCTION_URL] \
  -H "Content-Type: application/json" \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" \
  -d '{"gcs_file_path": "audiences/test_audience.json", "platforms": ["google_ads", "facebook"]}'
```

### Testing GCS Trigger

Upload a JSON file to the audiences folder in your bucket:

```bash
gsutil cp sample_data/san_diego_teachers.json gs://[BUCKET_NAME]/audiences/
```

## Step 6: Set Up Cloud Scheduler (Optional)

To run the audience deployment on a schedule:

```bash
gcloud scheduler jobs create http audience-deployment-daily \
  --schedule "0 6 * * *" \
  --uri [FUNCTION_URL] \
  --message-body '{"gcs_file_path": "audiences/daily_audience.json", "platforms": ["google_ads", "facebook", "bing", "tiktok", "amazon"]}' \
  --headers "Content-Type=application/json" \
  --oidc-service-account-email [SERVICE_ACCOUNT_EMAIL]
```

This sets up a daily job that runs at 6:00 AM.

## Monitoring and Logging

View logs for your Cloud Function:

```bash
gcloud functions logs read audience-deployment
```

Set up Cloud Monitoring alerts for function errors:

1. Go to the Google Cloud Console
2. Navigate to Monitoring > Alerting
3. Create a new alert for Cloud Function errors
