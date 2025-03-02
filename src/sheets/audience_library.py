import logging
from typing import Dict, Any, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

logger = logging.getLogger('audience_deployment.sheets')

def get_sheets_client(config: Dict[str, Any]) -> Optional[gspread.Client]:
    """
    Get authenticated Google Sheets client.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Optional[gspread.Client]: Authenticated gspread client or None if authentication fails
    """
    try:
        # Get credentials file path from config
        credentials_file = config['google_sheets']['credentials_file']
        
        # Define the required scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Authenticate with service account
        credentials = Credentials.from_service_account_file(
            credentials_file, 
            scopes=scopes
        )
        
        # Create gspread client
        client = gspread.authorize(credentials)
        return client
    
    except Exception as e:
        logger.exception(f"Error authenticating with Google Sheets: {str(e)}")
        return None

def update_audience_library(platform: str, audience_name: str, created_date: str, config: Dict[str, Any]) -> bool:
    """
    Update audience library in Google Sheets.
    
    Args:
        platform (str): Ad platform name
        audience_name (str): Name of the audience
        created_date (str): Date when the audience was created (YYYY-MM-DD)
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Get Google Sheets client
        client = get_sheets_client(config)
        if not client:
            logger.error("Failed to get Google Sheets client")
            return False
        
        # Get spreadsheet and worksheet
        spreadsheet_id = config['google_sheets']['audience_library_id']
        worksheet_name = config['google_sheets']['worksheet_name']
        
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.worksheet(worksheet_name)
        except SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {spreadsheet_id}")
            return False
        except WorksheetNotFound:
            logger.error(f"Worksheet not found: {worksheet_name}")
            return False
        
        # Check if the audience already exists
        try:
            # Find rows that match platform and audience name
            cell_list = worksheet.findall(audience_name)
            matching_rows = []
            
            for cell in cell_list:
                row = cell.row
                platform_cell = worksheet.cell(row, 1).value  # Assuming platform is in column A
                
                if platform_cell == platform:
                    matching_rows.append(row)
            
            # Get current date for the last updated field
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            if matching_rows:
                # Update existing row
                row = matching_rows[0]
                worksheet.update_cell(row, 4, current_date)  # Assuming Last Updated is in column D
                logger.info(f"Updated existing audience in library: {platform} - {audience_name}")
            else:
                # Add new row
                new_row = [platform, audience_name, created_date, current_date]
                worksheet.append_row(new_row)
                logger.info(f"Added new audience to library: {platform} - {audience_name}")
            
            return True
        
        except Exception as e:
            logger.exception(f"Error updating worksheet: {str(e)}")
            return False
    
    except Exception as e:
        logger.exception(f"Error updating audience library: {str(e)}")
        return False
