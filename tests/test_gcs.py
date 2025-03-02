import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.storage.gcs import download_audience_data


class TestGCS(unittest.TestCase):
    """Test cases for Google Cloud Storage functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'gcp': {
                'project_id': 'test-project',
                'bucket_name': 'test-bucket'
            }
        }
        
        self.test_audience_data = {
            'name': 'Test Audience',
            'description': 'Test audience for unit tests',
            'users': [
                {
                    'email': 'test_email_hash_1',
                    'phone': 'test_phone_hash_1'
                },
                {
                    'email': 'test_email_hash_2',
                    'phone': 'test_phone_hash_2'
                }
            ]
        }

    @patch('google.cloud.storage.Client')
    def test_download_audience_data_success(self, mock_storage_client):
        """Test successful download of audience data from GCS."""
        # Set up mocks
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.return_value = json.dumps(self.test_audience_data)
        
        # Call the function
        result = download_audience_data('test/path.json', self.config)
        
        # Verify the result
        self.assertEqual(result, self.test_audience_data)
        mock_storage_client.return_value.bucket.assert_called_once_with('test-bucket')
        mock_bucket.blob.assert_called_once_with('test/path.json')
        mock_blob.download_as_text.assert_called_once()

    @patch('google.cloud.storage.Client')
    def test_download_audience_data_failure(self, mock_storage_client):
        """Test handling of download failure from GCS."""
        # Set up mocks to simulate an error
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.download_as_text.side_effect = Exception("Test error")
        
        # Call the function
        result = download_audience_data('test/path.json', self.config)
        
        # Verify the result is None on error
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
