#!/bin/bash
# Script to deploy the Audience Deployment Cloud Functions to GCP

# Default values
RUNTIME="python310"
MEMORY="512MB"
TIMEOUT="300s"
REGION="us-central1"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --bucket)
      BUCKET_NAME="$2"
      shift 2
      ;;
    --service-account)
      SERVICE_ACCOUNT="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --env-secret)
      ENV_SECRET="$2"
      shift 2
      ;;
    --memory)
      MEMORY="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --runtime)
      RUNTIME="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --project PROJECT_ID         GCP Project ID (required)"
      echo "  --bucket BUCKET_NAME         GCS Bucket Name (required)"
      echo "  --service-account EMAIL      Service Account Email (required)"
      echo "  --env-secret SECRET_NAME     Secret Manager Secret Name (required)"
      echo "  --region REGION              GCP Region (default: us-central1)"
      echo "  --memory MEMORY              Memory allocation (default: 512MB)"
      echo "  --timeout TIMEOUT            Function timeout (default: 300s)"
      echo "  --runtime RUNTIME            Python runtime (default: python310)"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check required arguments
if [ -z "$PROJECT_ID" ] || [ -z "$BUCKET_NAME" ] || [ -z "$SERVICE_ACCOUNT" ] || [ -z "$ENV_SECRET" ]; then
  echo "Error: Missing required arguments"
  echo "Run '$0 --help' for usage information"
  exit 1
fi

# Set project
echo "Setting GCP project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Deploy HTTP-triggered function
echo "Deploying HTTP-triggered Cloud Function..."
gcloud functions deploy audience-deployment-http \
  --runtime $RUNTIME \
  --trigger-http \
  --entry-point process_audience \
  --memory $MEMORY \
  --timeout $TIMEOUT \
  --region $REGION \
  --set-secrets "ENV_FILE=$ENV_SECRET:latest" \
  --service-account $SERVICE_ACCOUNT \
  --allow-unauthenticated

# Check if HTTP deployment was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to deploy HTTP-triggered function"
  exit 1
fi

# Get the HTTP function URL
HTTP_URL=$(gcloud functions describe audience-deployment-http --region $REGION --format="value(httpsTrigger.url)")
echo "HTTP function deployed successfully at: $HTTP_URL"

# Deploy GCS-triggered function
echo "Deploying GCS-triggered Cloud Function..."
gcloud functions deploy audience-deployment-gcs \
  --runtime $RUNTIME \
  --trigger-event google.storage.object.finalize \
  --trigger-resource $BUCKET_NAME \
  --entry-point process_gcs_trigger \
  --memory $MEMORY \
  --timeout $TIMEOUT \
  --region $REGION \
  --set-secrets "ENV_FILE=$ENV_SECRET:latest" \
  --service-account $SERVICE_ACCOUNT

# Check if GCS deployment was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to deploy GCS-triggered function"
  exit 1
fi

echo "GCS-triggered function deployed successfully"
echo "Deployment complete!"

# Provide next steps
echo ""
echo "Next steps:"
echo "1. Test the HTTP function with:"
echo "   curl -X POST $HTTP_URL -H \"Content-Type: application/json\" -d '{\"gcs_file_path\": \"audiences/test_audience.json\", \"platforms\": [\"google_ads\", \"facebook\"]}'"
echo ""
echo "2. Test the GCS trigger by uploading a file:"
echo "   gsutil cp sample_data/san_diego_teachers.json gs://$BUCKET_NAME/audiences/"
echo ""
echo "3. Set up Cloud Scheduler jobs (optional):"
echo "   python scripts/setup_cloud_scheduler.py --function-url $HTTP_URL --service-account $SERVICE_ACCOUNT --project-id $PROJECT_ID"
