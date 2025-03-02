import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


class MockRequest:
    """Mock Flask request object for testing."""
    
    def __init__(self, json_data=None):
        self.json_data = json_data
    
    def get_json(self, silent=False):
        return self.json_data


class TestMain(unittest.TestCase):
    """Test cases for the main Cloud Function."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_request_data = {
            'gcs_file_path': 'audiences/test_audience.json',
            'platforms': ['google_ads', 'facebook']
        }
        
        self.audience_data = {
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
        
        self.config = {
            'gcp': {
                'project_id': 'test-project',
                'bucket_name': 'test-bucket'
            },
            'google_ads': {
                'client_id': 'test-client-id',
                'customer_ids': ['123456789']
            },
            'facebook': {
                'app_id': 'test-app-id',
                'account_id': 'test-account-id'
            }
        }

    @patch('main.load_config')
    @patch('main.download_audience_data')
    @patch('main.upload_to_google_ads')
    @patch('main.upload_to_facebook')
    @patch('main.update_audience_library')
    def test_process_audience_success(self, mock_update_library, mock_upload_facebook, 
                                     mock_upload_google_ads, mock_download_data, mock_load_config):
        """Test successful processing of audience data."""
        # Set up mocks
        mock_load_config.return_value = self.config
        mock_download_data.return_value = self.audience_data
        mock_upload_google_ads.return_value = {'success': True, 'results': {'123456789': {'success': True}}}
        mock_upload_facebook.return_value = {'success': True, 'audience_id': 'test_audience_id'}
        mock_update_library.return_value = True
        
        # Create request
        request = MockRequest(self.valid_request_data)
        
        # Call the function
        response = main.process_audience(request)
        
        # Verify the response
        self.assertTrue(response['success'])
        self.assertEqual(response['audience_name'], 'Test Audience')
        self.assertEqual(len(response['results']), 2)
        self.assertTrue(response['results']['google_ads']['success'])
        self.assertTrue(response['results']['facebook']['success'])
        
        # Verify function calls
        mock_load_config.assert_called_once()
        mock_download_data.assert_called_once_with('audiences/test_audience.json', self.config)
        mock_upload_google_ads.assert_called_once_with(self.audience_data, self.config)
        mock_upload_facebook.assert_called_once_with(self.audience_data, self.config)
        self.assertEqual(mock_update_library.call_count, 2)  # Called once for each successful platform

    @patch('main.load_config')
    def test_process_audience_missing_parameters(self, mock_load_config):
        """Test handling of missing parameters in request."""
        # Set up mock
        mock_load_config.return_value = self.config
        
        # Test missing gcs_file_path
        request = MockRequest({'platforms': ['google_ads']})
        response, status_code = main.process_audience(request)
        self.assertFalse(response['success'])
        self.assertEqual(status_code, 400)
        
        # Test missing platforms
        request = MockRequest({'gcs_file_path': 'audiences/test.json'})
        response, status_code = main.process_audience(request)
        self.assertFalse(response['success'])
        self.assertEqual(status_code, 400)
        
        # Test empty request
        request = MockRequest({})
        response, status_code = main.process_audience(request)
        self.assertFalse(response['success'])
        self.assertEqual(status_code, 400)
        
        # Test null request
        request = MockRequest(None)
        response, status_code = main.process_audience(request)
        self.assertFalse(response['success'])
        self.assertEqual(status_code, 400)

    @patch('main.load_config')
    @patch('main.download_audience_data')
    def test_process_audience_download_failure(self, mock_download_data, mock_load_config):
        """Test handling of audience data download failure."""
        # Set up mocks
        mock_load_config.return_value = self.config
        mock_download_data.return_value = None  # Simulate download failure
        
        # Create request
        request = MockRequest(self.valid_request_data)
        
        # Call the function
        response, status_code = main.process_audience(request)
        
        # Verify the response
        self.assertFalse(response['success'])
        self.assertEqual(status_code, 500)
        self.assertIn('Failed to download audience data', response['error'])

    @patch('main.load_config')
    @patch('main.download_audience_data')
    @patch('main.upload_to_google_ads')
    @patch('main.upload_to_facebook')
    def test_process_audience_partial_success(self, mock_upload_facebook, mock_upload_google_ads, 
                                             mock_download_data, mock_load_config):
        """Test handling of partial success (one platform succeeds, one fails)."""
        # Set up mocks
        mock_load_config.return_value = self.config
        mock_download_data.return_value = self.audience_data
        mock_upload_google_ads.return_value = {'success': True, 'results': {'123456789': {'success': True}}}
        mock_upload_facebook.return_value = {'success': False, 'error': 'API error'}
        
        # Create request
        request = MockRequest(self.valid_request_data)
        
        # Call the function
        response = main.process_audience(request)
        
        # Verify the response
        self.assertTrue(response['success'])  # Overall success is true if any platform succeeds
        self.assertEqual(response['audience_name'], 'Test Audience')
        self.assertTrue(response['results']['google_ads']['success'])
        self.assertFalse(response['results']['facebook']['success'])


if __name__ == '__main__':
    unittest.main()
