# Deployment Guide for Audience Deployment Automation System

This guide provides step-by-step instructions for deploying the Audience Deployment Automation System on Google Cloud Platform (GCP).

## Prerequisites

1. Google Cloud Platform account with billing enabled
2. Google Cloud SDK installed on your local machine
3. Python 3.9+ installed on your local machine
4. API access to advertising platforms (Google Ads, Facebook, Bing, TikTok, Amazon)
5. Google Sheets API access and service account

## Step 1: Set Up Google Cloud Project

1. Create a new GCP project or use an existing one:

```bash
gcloud projects create [PROJECT_ID] --name="Audience Deployment Automation"
gcloud config set project [PROJECT_ID]
```

2. Enable required APIs:

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable sheets.googleapis.com
```

## Step 2: Create Google Cloud Storage Bucket

1. Create a GCS bucket to store audience data:

```bash
gsutil mb -l [REGION] gs://[BUCKET_NAME]
```

Replace `[REGION]` with your preferred region (e.g., `us-central1`) and `[BUCKET_NAME]` with a unique bucket name.

## Step 3: Configure Authentication and API Keys

1. Create a `.env` file by copying the `.env.example` file:

```bash
cp .env.example .env
```

2. Fill in the `.env` file with your API keys and credentials for each platform.

3. For Google Sheets integration, create a service account:

```bash
gcloud iam service-accounts create audience-sheets-sa \
    --display-name="Audience Sheets Service Account"
```

4. Generate and download a key for the service account:

```bash
gcloud iam service-accounts keys create credentials.json \
    --iam-account=audience-sheets-sa@[PROJECT_ID].iam.gserviceaccount.com
```

5. Share your Google Sheet with the service account email address and give it edit permissions.

6. Update the `.env` file with the path to the credentials file and the Google Sheet ID.

## Step 4: Deploy the Cloud Function

1. Deploy the Cloud Function using the Google Cloud SDK:

```bash
gcloud functions deploy process_audience \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point process_audience \
    --source . \
    --env-vars-file .env.yaml
```

Note: Before running this command, convert your `.env` file to `.env.yaml` format.

2. After deployment, you'll receive a URL for the Cloud Function. Save this URL as you'll need it to trigger the function.

## Step 5: Test the Deployment

1. Create a sample audience JSON file:

```json
{
  "name": "Test Audience",
  "description": "Test audience for deployment verification",
  "users": [
    {
      "email": "hashed_email_1",
      "phone": "hashed_phone_1",
      "address": {
        "first_name": "hashed_first_name_1",
        "last_name": "hashed_last_name_1",
        "country_code": "US",
        "postal_code": "12345"
      }
    },
    {
      "email": "hashed_email_2",
      "phone": "hashed_phone_2"
    }
  ]
}
```

2. Upload the sample file to your GCS bucket:

```bash
gsutil cp sample_audience.json gs://[BUCKET_NAME]/audiences/
```

3. Trigger the Cloud Function using curl:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"gcs_file_path": "audiences/sample_audience.json", "platforms": ["google_ads", "facebook"]}' \
  [CLOUD_FUNCTION_URL]
```

Replace `[CLOUD_FUNCTION_URL]` with the URL of your deployed Cloud Function.

## Step 6: Set Up Scheduled Execution (Optional)

If you want to run the audience deployment on a schedule, you can use Cloud Scheduler:

1. Enable the Cloud Scheduler API:

```bash
gcloud services enable cloudscheduler.googleapis.com
```

2. Create a scheduler job:

```bash
gcloud scheduler jobs create http audience-deployment-job \
    --schedule="0 0 * * *" \
    --uri="[CLOUD_FUNCTION_URL]" \
    --message-body='{"gcs_file_path": "audiences/daily_audience.json", "platforms": ["google_ads", "facebook", "bing", "tiktok", "amazon"]}' \
    --headers="Content-Type=application/json"
```

This will run the job daily at midnight.

## Troubleshooting

- Check Cloud Logging for error messages:

```bash
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=process_audience"
```

- Verify that your API keys and credentials are correct.
- Ensure that the service account has the necessary permissions.
- Check that the audience data JSON file is properly formatted.

## Security Considerations

- Consider using Secret Manager to store API keys and credentials instead of environment variables.
- Set up IAM permissions to restrict access to the Cloud Function.
- Enable Cloud Function authentication to prevent unauthorized access.
- Implement IP-based restrictions for additional security.

## Maintenance

- Regularly update dependencies to patch security vulnerabilities.
- Monitor API usage to avoid hitting rate limits.
- Set up alerts for function errors or failures.
- Periodically review and rotate API keys and credentials.
