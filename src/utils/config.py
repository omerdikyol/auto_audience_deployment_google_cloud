import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and/or config file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Try to load config from config.json
    config_path = os.environ.get('CONFIG_PATH', 'config/config.json')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # If config file doesn't exist, create config from environment variables
        config = {
            "gcp": {
                "project_id": os.environ.get('GCP_PROJECT_ID'),
                "bucket_name": os.environ.get('GCS_BUCKET_NAME'),
                "region": os.environ.get('GCP_REGION', 'us-central1')
            },
            "google_ads": {
                "client_id": os.environ.get('GOOGLE_ADS_CLIENT_ID'),
                "client_secret": os.environ.get('GOOGLE_ADS_CLIENT_SECRET'),
                "refresh_token": os.environ.get('GOOGLE_ADS_REFRESH_TOKEN'),
                "developer_token": os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN'),
                "login_customer_id": os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID'),
                "customer_ids": os.environ.get('GOOGLE_ADS_CUSTOMER_IDS', '').split(',')
            },
            "facebook": {
                "app_id": os.environ.get('FACEBOOK_APP_ID'),
                "app_secret": os.environ.get('FACEBOOK_APP_SECRET'),
                "access_token": os.environ.get('FACEBOOK_ACCESS_TOKEN'),
                "account_id": os.environ.get('FACEBOOK_ACCOUNT_ID')
            },
            "bing": {
                "client_id": os.environ.get('BING_CLIENT_ID'),
                "client_secret": os.environ.get('BING_CLIENT_SECRET'),
                "developer_token": os.environ.get('BING_DEVELOPER_TOKEN'),
                "refresh_token": os.environ.get('BING_REFRESH_TOKEN'),
                "account_id": os.environ.get('BING_ACCOUNT_ID')
            },
            "tiktok": {
                "app_id": os.environ.get('TIKTOK_APP_ID'),
                "app_secret": os.environ.get('TIKTOK_APP_SECRET'),
                "access_token": os.environ.get('TIKTOK_ACCESS_TOKEN'),
                "advertiser_id": os.environ.get('TIKTOK_ADVERTISER_ID')
            },
            "amazon": {
                "client_id": os.environ.get('AMAZON_CLIENT_ID'),
                "client_secret": os.environ.get('AMAZON_CLIENT_SECRET'),
                "refresh_token": os.environ.get('AMAZON_REFRESH_TOKEN'),
                "profile_id": os.environ.get('AMAZON_PROFILE_ID'),
                "region": os.environ.get('AMAZON_REGION')
            },
            "google_sheets": {
                "credentials_file": os.environ.get('GOOGLE_SHEETS_CREDENTIALS_FILE'),
                "audience_library_id": os.environ.get('GOOGLE_SHEETS_AUDIENCE_LIBRARY_ID'),
                "worksheet_name": os.environ.get('GOOGLE_SHEETS_WORKSHEET_NAME', 'Audience Library')
            },
            "logging": {
                "level": os.environ.get('LOGGING_LEVEL', 'INFO')
            }
        }
    
    return config
