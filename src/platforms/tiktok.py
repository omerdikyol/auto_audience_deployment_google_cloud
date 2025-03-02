import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger('audience_deployment.platforms.tiktok')

# TikTok API endpoints
TIKTOK_API_BASE = 'https://business-api.tiktok.com/open_api/v1.3'
CUSTOM_AUDIENCE_CREATE_URL = f'{TIKTOK_API_BASE}/audience/custom/create/'
CUSTOM_AUDIENCE_USERS_URL = f'{TIKTOK_API_BASE}/audience/custom/users/'

def get_tiktok_headers(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get headers for TikTok API requests.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dict[str, str]: Headers for TikTok API requests
    """
    access_token = config['tiktok']['access_token']
    
    return {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }

def create_custom_audience(
    advertiser_id: str,
    audience_name: str,
    audience_description: str,
    headers: Dict[str, str]
) -> str:
    """
    Create a new Custom Audience in TikTok.
    
    Args:
        advertiser_id (str): TikTok advertiser ID
        audience_name (str): Name of the audience
        audience_description (str): Description of the audience
        headers (Dict[str, str]): Headers for TikTok API requests
        
    Returns:
        str: ID of the created custom audience
    """
    payload = {
        'advertiser_id': advertiser_id,
        'custom_audience_name': audience_name,
        'description': audience_description
    }
    
    response = requests.post(CUSTOM_AUDIENCE_CREATE_URL, headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code == 200 and response_data.get('code') == 0:
        return response_data.get('data', {}).get('audience_id')
    else:
        error_message = response_data.get('message', 'Unknown error')
        logger.error(f"Error creating TikTok custom audience: {error_message}")
        return None

def add_users_to_custom_audience(
    advertiser_id: str,
    audience_id: str,
    users: List[Dict[str, Any]],
    headers: Dict[str, str]
) -> bool:
    """
    Add users to a TikTok Custom Audience.
    
    Args:
        advertiser_id (str): TikTok advertiser ID
        audience_id (str): ID of the custom audience
        users (List[Dict[str, Any]]): List of user data dictionaries
        headers (Dict[str, str]): Headers for TikTok API requests
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare user data for TikTok
    audience_data = []
    
    for user in users:
        if 'email' in user:
            audience_data.append({
                'type': 'EMAIL',
                'value': user['email']
            })
        
        if 'phone' in user:
            audience_data.append({
                'type': 'PHONE_NUMBER',
                'value': user['phone']
            })
    
    if not audience_data:
        logger.error("No valid user data found for TikTok")
        return False
    
    # Add users to the custom audience
    payload = {
        'advertiser_id': advertiser_id,
        'audience_id': audience_id,
        'action': 'ADD',
        'id_schema': 'CUSTOM',
        'id_data': audience_data
    }
    
    response = requests.post(CUSTOM_AUDIENCE_USERS_URL, headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code == 200 and response_data.get('code') == 0:
        return True
    else:
        error_message = response_data.get('message', 'Unknown error')
        logger.error(f"Error adding users to TikTok custom audience: {error_message}")
        return False

def upload_to_tiktok(audience_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload audience data to TikTok.
    
    Args:
        audience_data (Dict[str, Any]): Audience data
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dict[str, Any]: Result of the upload operation
    """
    try:
        # Extract audience info
        audience_name = audience_data.get('name', 'Unnamed Audience')
        audience_description = audience_data.get('description', f'Audience created on {datetime.now().strftime("%Y-%m-%d")}')
        users = audience_data.get('users', [])
        
        if not users:
            logger.error(f"No users found in audience data for {audience_name}")
            return {"success": False, "error": "No users found in audience data"}
        
        # Get TikTok API headers
        headers = get_tiktok_headers(config)
        
        # Get advertiser ID from config
        advertiser_id = config['tiktok']['advertiser_id']
        
        if not advertiser_id:
            logger.error("No TikTok advertiser ID found in config")
            return {"success": False, "error": "No TikTok advertiser ID found in config"}
        
        try:
            # Create a new custom audience
            audience_id = create_custom_audience(
                advertiser_id=advertiser_id,
                audience_name=audience_name,
                audience_description=audience_description,
                headers=headers
            )
            
            if not audience_id:
                logger.error(f"Failed to create custom audience in TikTok: {audience_name}")
                return {"success": False, "error": "Failed to create custom audience"}
            
            # Add users to the custom audience
            success = add_users_to_custom_audience(
                advertiser_id=advertiser_id,
                audience_id=audience_id,
                users=users,
                headers=headers
            )
            
            if success:
                logger.info(f"Successfully created audience in TikTok: {audience_name}")
                return {
                    "success": True,
                    "audience_id": audience_id
                }
            else:
                logger.error(f"Failed to add users to TikTok custom audience: {audience_name}")
                return {"success": False, "error": "Failed to add users to custom audience"}
        
        except Exception as e:
            error_message = f"Error creating audience in TikTok: {str(e)}"
            logger.exception(error_message)
            return {"success": False, "error": error_message}
    
    except Exception as e:
        logger.exception(f"Unhandled exception in upload_to_tiktok: {str(e)}")
        return {"success": False, "error": str(e)}
