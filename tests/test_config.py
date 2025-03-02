import unittest
import os
import json
from unittest.mock import patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.config import load_config


class TestConfig(unittest.TestCase):
    """Test cases for configuration loading functionality."""

    @patch.dict(os.environ, {
        'GCP_PROJECT_ID': 'test-project',
        'GCS_BUCKET_NAME': 'test-bucket',
        'GOOGLE_ADS_CLIENT_ID': 'test-client-id',
        'FACEBOOK_APP_ID': 'test-app-id',
        'BING_CLIENT_ID': 'test-bing-id',
        'TIKTOK_APP_ID': 'test-tiktok-id',
        'AMAZON_CLIENT_ID': 'test-amazon-id',
        'GOOGLE_SHEETS_AUDIENCE_LIBRARY_ID': 'test-sheet-id'
    })
    def test_load_config_from_env(self):
        """Test loading configuration from environment variables."""
        # Mock that config file doesn't exist
        with patch('os.path.exists', return_value=False):
            config = load_config()
            
            # Verify config values from environment
            self.assertEqual(config['gcp']['project_id'], 'test-project')
            self.assertEqual(config['gcp']['bucket_name'], 'test-bucket')
            self.assertEqual(config['google_ads']['client_id'], 'test-client-id')
            self.assertEqual(config['facebook']['app_id'], 'test-app-id')
            self.assertEqual(config['bing']['client_id'], 'test-bing-id')
            self.assertEqual(config['tiktok']['app_id'], 'test-tiktok-id')
            self.assertEqual(config['amazon']['client_id'], 'test-amazon-id')
            self.assertEqual(config['google_sheets']['audience_library_id'], 'test-sheet-id')

    @patch('os.path.exists', return_value=True)
    def test_load_config_from_file(self, mock_exists):
        """Test loading configuration from config file."""
        mock_config = {
            'gcp': {
                'project_id': 'file-project',
                'bucket_name': 'file-bucket'
            },
            'google_ads': {
                'client_id': 'file-client-id'
            },
            'facebook': {
                'app_id': 'file-app-id'
            },
            'bing': {
                'client_id': 'file-bing-id'
            },
            'tiktok': {
                'app_id': 'file-tiktok-id'
            },
            'amazon': {
                'client_id': 'file-amazon-id'
            },
            'google_sheets': {
                'audience_library_id': 'file-sheet-id'
            },
            'logging': {
                'level': 'DEBUG'
            }
        }
        
        # Mock open to return our test config
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            config = load_config()
            
            # Verify config values from file
            self.assertEqual(config['gcp']['project_id'], 'file-project')
            self.assertEqual(config['gcp']['bucket_name'], 'file-bucket')
            self.assertEqual(config['google_ads']['client_id'], 'file-client-id')
            self.assertEqual(config['facebook']['app_id'], 'file-app-id')
            self.assertEqual(config['bing']['client_id'], 'file-bing-id')
            self.assertEqual(config['tiktok']['app_id'], 'file-tiktok-id')
            self.assertEqual(config['amazon']['client_id'], 'file-amazon-id')
            self.assertEqual(config['google_sheets']['audience_library_id'], 'file-sheet-id')
            self.assertEqual(config['logging']['level'], 'DEBUG')


if __name__ == '__main__':
    unittest.main()
