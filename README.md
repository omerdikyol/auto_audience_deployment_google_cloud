<h1 align="center">Audience deployment on Google Cloud</h1>

<p align="center">
  <img alt="language: Python" src="https://img.shields.io/badge/language-Python-3776AB">
  <img alt="platform: Google Cloud" src="https://img.shields.io/badge/platform-Google%20Cloud-4285F4">
  <img alt="status: prototype" src="https://img.shields.io/badge/status-prototype-yellow">
</p>

An integration prototype that reads audience JSON from Google Cloud Storage, dispatches it to advertising-platform adapters, and records results in Google Sheets. HTTP, storage-event, and scheduled entry points share the processing workflow.

## Integration status

The adapters are experimental. The mocked tests exercise orchestration, not successful uploads to every vendor. Validate each adapter against the relevant provider sandbox before deploying it; the Google Ads adapter currently needs a missing `datetime` import corrected.

Start with [main.py](main.py) for the trigger flow, [sample_data](sample_data) for input examples, and [the deployment guide](docs/gcp_deployment.md) for infrastructure setup.

## Features

- **Platform adapters** in the source: Google Ads, Facebook Ads, Instagram Ads (via the Facebook Marketing API), Bing Ads, TikTok Ads, Amazon Ads
- **Flexible Triggering Options**:
  - HTTP API endpoints for on-demand audience deployment
  - Automatic processing via GCS event triggers when new audience files are uploaded
  - Scheduled deployments using Cloud Scheduler
- **Centralized Management**: Maintain an audience library in Google Sheets with deployment status
- Configuration through environment variables and Secret Manager integration
- Logging through Google Cloud Logging
- Error reporting for the processing workflow
- Mocked tests for configuration, Storage, Sheets, and the entry-point workflow

## Project structure

| Path | Contents |
| --- | --- |
| `main.py` | Cloud Function entry points (HTTP, GCS event, scheduled) |
| `src/platforms/` | Adapters: `google_ads.py`, `facebook.py` (Facebook and Instagram), `bing.py`, `tiktok.py`, `amazon.py` |
| `src/sheets/audience_library.py` | Audience library and deployment status in Google Sheets |
| `src/storage/gcs.py` | GCS file operations |
| `src/utils/` | Config loading, logging setup, local testing helpers |
| `config/` | Example configuration and scheduler configuration |
| `docs/` | `deployment.md` and `gcp_deployment.md` |
| `sample_data/` | Example audience files (`san_diego_teachers.json`, `la_students.json`) |
| `scripts/` | `deploy_function.sh`, `setup_cloud_scheduler.py` |
| `tests/` | Mocked tests for config, GCS, Sheets, and the entry point; run with `run_tests.py` |

## Getting Started

### Prerequisites

- Python 3.9+ installed locally for development
- Google Cloud Platform account with billing enabled
- API access to the advertising platforms you plan to use
- Google Cloud SDK installed and configured

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/omerdikyol/auto_audience_deployment_google_cloud.git
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
