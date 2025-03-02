# Audience Deployment Automation System

A serverless automation system built on Google Cloud Platform for deploying audience data to multiple advertising platforms.

## Features

- Read JSON audience data from Google Cloud Storage (GCS)
- Process and send audience data to multiple advertising platforms:
  - Google Ads
  - Facebook Ads
  - Instagram Ads (via Facebook Marketing API)
  - Bing Ads
  - TikTok Ads
  - Amazon Ads
- Maintain an audience library in Google Sheets
- Secure configuration management
- Comprehensive error logging via Google Cloud Logging

## Project Structure

```
auto_audience_deployment_google_cloud/
├── config/                  # Configuration files
│   └── config.json.example  # Example configuration file
├── docs/                    # Documentation
├── src/                     # Source code
│   ├── platforms/           # Platform-specific integrations
│   ├── sheets/              # Google Sheets integration
│   ├── storage/             # GCS integration
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── .env.example             # Example environment variables file
├── main.py                  # Main entry point
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Setup and Deployment

See the [deployment guide](docs/deployment.md) for detailed instructions on setting up and deploying this system on Google Cloud Platform.

## Requirements

- Python 3.9+
- Google Cloud Platform account
- API access to advertising platforms

## License

Proprietary - All rights reserved
