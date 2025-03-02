import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.sheets.audience_library import update_audience_library, get_sheets_client


class TestSheets(unittest.TestCase):
    """Test cases for Google Sheets integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'google_sheets': {
                'credentials_file': 'test_credentials.json',
                'audience_library_id': 'test_spreadsheet_id',
                'worksheet_name': 'Test Worksheet'
            }
        }

    @patch('gspread.authorize')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_get_sheets_client_success(self, mock_credentials, mock_authorize):
        """Test successful creation of Google Sheets client."""
        # Set up mocks
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        
        # Call the function
        result = get_sheets_client(self.config)
        
        # Verify the result
        self.assertEqual(result, mock_client)
        mock_credentials.assert_called_once_with(
            'test_credentials.json', 
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        mock_authorize.assert_called_once()

    @patch('gspread.authorize')
    @patch('google.oauth2.service_account.Credentials.from_service_account_file')
    def test_get_sheets_client_failure(self, mock_credentials, mock_authorize):
        """Test handling of client creation failure."""
        # Set up mocks to simulate an error
        mock_credentials.side_effect = Exception("Test error")
        
        # Call the function
        result = get_sheets_client(self.config)
        
        # Verify the result is None on error
        self.assertIsNone(result)

    @patch('src.sheets.audience_library.get_sheets_client')
    def test_update_audience_library_success(self, mock_get_client):
        """Test successful update of audience library."""
        # Set up mocks
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock that audience doesn't exist yet
        mock_worksheet.findall.return_value = []
        
        # Call the function
        result = update_audience_library(
            platform='test_platform',
            audience_name='test_audience',
            created_date='2025-03-02',
            config=self.config
        )
        
        # Verify the result and function calls
        self.assertTrue(result)
        mock_get_client.assert_called_once_with(self.config)
        mock_client.open_by_key.assert_called_once_with('test_spreadsheet_id')
        mock_spreadsheet.worksheet.assert_called_once_with('Test Worksheet')
        mock_worksheet.findall.assert_called_once_with('test_audience')
        mock_worksheet.append_row.assert_called_once()

    @patch('src.sheets.audience_library.get_sheets_client')
    def test_update_audience_library_existing(self, mock_get_client):
        """Test update of existing audience in library."""
        # Set up mocks
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_cell = MagicMock()
        mock_platform_cell = MagicMock()
        
        mock_get_client.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock that audience exists
        mock_cell.row = 2
        mock_worksheet.findall.return_value = [mock_cell]
        mock_worksheet.cell.return_value = mock_platform_cell
        mock_platform_cell.value = 'test_platform'
        
        # Call the function
        result = update_audience_library(
            platform='test_platform',
            audience_name='test_audience',
            created_date='2025-03-02',
            config=self.config
        )
        
        # Verify the result and function calls
        self.assertTrue(result)
        mock_worksheet.update_cell.assert_called_once()
        # Should not append a new row
        mock_worksheet.append_row.assert_not_called()


if __name__ == '__main__':
    unittest.main()
