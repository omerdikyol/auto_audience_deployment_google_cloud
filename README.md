# Audience Deployment Automation System

A serverless automation system built on Google Cloud Platform for deploying audience data to multiple advertising platforms. This system automatically processes audience data from JSON files stored in Google Cloud Storage and deploys them to various advertising platforms while maintaining a centralized audience library in Google Sheets.

## Features

- **Multi-Platform Support**: Deploy audiences to multiple advertising platforms:
  - Google Ads
  - Facebook Ads
  - Instagram Ads (via Facebook Marketing API)
  - Bing Ads
  - TikTok Ads
  - Amazon Ads
- **Flexible Triggering Options**:
  - HTTP API endpoints for on-demand audience deployment
  - Automatic processing via GCS event triggers when new audience files are uploaded
  - Scheduled deployments using Cloud Scheduler
- **Centralized Management**: Maintain an audience library in Google Sheets with deployment status
- **Secure Configuration**: Environment variables and Secret Manager integration for API credentials
- **Comprehensive Logging**: Detailed logging via Google Cloud Logging
- **Error Handling**: Robust error handling and reporting
- **Testing**: Unit tests for all components

## Project Structure

```
auto_audience_deployment_google_cloud/
├── config/                       # Configuration files
│   ├── config.json.example       # Example configuration file
│   └── scheduler_config.json.example # Example scheduler configuration
├── docs/                         # Documentation
│   ├── deployment.md             # General deployment guide
│   └── gcp_deployment.md         # GCP-specific deployment instructions
├── sample_data/                  # Sample audience data for testing
│   ├── san_diego_teachers.json   # Sample audience data
│   └── la_students.json          # Sample audience data
├── scripts/                      # Utility scripts
│   ├── deploy_function.sh        # Script to deploy Cloud Functions
│   └── setup_cloud_scheduler.py  # Script to set up Cloud Scheduler jobs
├── src/                          # Source code
│   ├── platforms/                # Platform-specific integrations
│   │   ├── amazon.py             # Amazon Ads integration
│   │   ├── bing.py               # Bing Ads integration
│   │   ├── facebook.py           # Facebook/Instagram Ads integration
│   │   ├── google_ads.py         # Google Ads integration
│   │   └── tiktok.py             # TikTok Ads integration
│   ├── sheets/                   # Google Sheets integration
│   │   └── audience_library.py   # Audience library management
│   ├── storage/                  # GCS integration
│   │   └── gcs.py                # GCS file operations
│   └── utils/                    # Utility functions
│       ├── config.py             # Configuration loading
│       ├── local_testing.py      # Local testing utilities
│       └── logging_setup.py      # Logging configuration
├── tests/                        # Test files
│   ├── test_config.py            # Tests for configuration loading
│   ├── test_gcs.py               # Tests for GCS integration
│   ├── test_main.py              # Tests for main Cloud Function
│   └── test_sheets.py            # Tests for Google Sheets integration
├── .env.example                  # Example environment variables file
├── main.py                       # Main Cloud Function entry points
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── run_tests.py                  # Test runner script
```

## Getting Started

### Prerequisites

- Python 3.9+ installed locally for development
- Google Cloud Platform account with billing enabled
- API access to the advertising platforms you plan to use
- Google Cloud SDK installed and configured

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd auto_audience_deployment_google_cloud
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your API credentials and configuration

5. Run the tests to verify your setup:
   ```bash
   python run_tests.py
   ```

### Deployment Options

This system can be deployed in multiple ways:

1. **HTTP Trigger**: Deploy as an HTTP endpoint for on-demand processing
2. **GCS Trigger**: Deploy with a GCS trigger to automatically process new files
3. **Scheduled Jobs**: Set up Cloud Scheduler jobs for regular processing

See the [GCP Deployment Guide](docs/gcp_deployment.md) for detailed instructions.

## Usage

### Audience Data Format

Audience data should be stored as JSON files in the following format:

```json
{
  "name": "Audience Name",
  "description": "Audience description",
  "users": [
    {
      "email": "hashed_email_1",
      "phone": "hashed_phone_1"
    },
    {
      "email": "hashed_email_2",
      "phone": "hashed_phone_2"
    }
  ],
  "platforms": {
    "google_ads": {
      "customer_id": "123456789",
      "description": "Google Ads specific description"
    },
    "facebook": {
      "account_id": "987654321",
      "app_id": "fb_app_id"
    }
  }
}
```

### HTTP Endpoint

To trigger an audience deployment via the HTTP endpoint:

```bash
curl -X POST https://your-function-url -H "Content-Type: application/json" -d '{
  "gcs_file_path": "audiences/my_audience.json",
  "platforms": ["google_ads", "facebook"]
}'
```

### GCS Trigger

To trigger an audience deployment via GCS, simply upload a JSON file to the `audiences/` folder in your configured GCS bucket:

```bash
gsutil cp my_audience.json gs://your-bucket/audiences/
```

## Running Tests

Run all tests using the test runner script:

```bash
python run_tests.py
```

Or run individual test files:

```bash
python -m unittest tests/test_config.py
```

## Contributing

1. Create a new branch for your feature
2. Add tests for your changes
3. Ensure all tests pass
4. Submit a pull request

## License

Proprietary - All rights reserved
