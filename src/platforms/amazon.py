import logging
import requests
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger('audience_deployment.platforms.amazon')

# Amazon Advertising API endpoints
AMAZON_API_BASE = 'https://advertising-api.amazon.com/v2'

def get_amazon_access_token(config: Dict[str, Any]) -> str:
    """
    Get Amazon Advertising API access token.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        str: Access token
    """
    client_id = config['amazon']['client_id']
    client_secret = config['amazon']['client_secret']
    refresh_token = config['amazon']['refresh_token']
    
    url = 'https://api.amazon.com/auth/o2/token'
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(url, data=payload)
    response_data = response.json()
    
    if 'access_token' in response_data:
        return response_data['access_token']
    else:
        logger.error(f"Error getting Amazon access token: {response_data.get('error_description', 'Unknown error')}")
        return None

def get_amazon_headers(access_token: str, profile_id: str, region: str) -> Dict[str, str]:
    """
    Get headers for Amazon Advertising API requests.
    
    Args:
        access_token (str): Access token
        profile_id (str): Amazon Advertising profile ID
        region (str): Amazon Advertising region
        
    Returns:
        Dict[str, str]: Headers for Amazon Advertising API requests
    """
    return {
        'Authorization': f'Bearer {access_token}',
        'Amazon-Advertising-API-ClientId': profile_id,
        'Amazon-Advertising-API-Scope': profile_id,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Amazon-Advertising-API-Region': region
    }

def create_audience(
    audience_name: str,
    audience_description: str,
    headers: Dict[str, str]
) -> str:
    """
    Create a new Audience in Amazon Advertising.
    
    Args:
        audience_name (str): Name of the audience
        audience_description (str): Description of the audience
        headers (Dict[str, str]): Headers for Amazon Advertising API requests
        
    Returns:
        str: ID of the created audience
    """
    url = f'{AMAZON_API_BASE}/audiences'
    
    payload = {
        'name': audience_name,
        'description': audience_description,
        'audienceType': 'CUSTOMER_LIST'
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    
    if response.status_code == 200:
        return response_data.get('audienceId')
    else:
        error_message = response_data.get('message', 'Unknown error')
        logger.error(f"Error creating Amazon audience: {error_message}")
        return None

def add_users_to_audience(
    audience_id: str,
    users: List[Dict[str, Any]],
    headers: Dict[str, str]
) -> bool:
    """
    Add users to an Amazon Advertising Audience.
    
    Args:
        audience_id (str): ID of the audience
        users (List[Dict[str, Any]]): List of user data dictionaries
        headers (Dict[str, str]): Headers for Amazon Advertising API requests
        
    Returns:
        bool: True if successful, False otherwise
    """
    url = f'{AMAZON_API_BASE}/audiences/{audience_id}/users'
    
    # Prepare user data for Amazon
    audience_data = []
    
    for user in users:
        user_data = {}
        
        if 'email' in user:
            user_data['email'] = user['email']
        
        if user_data:
            audience_data.append(user_data)
    
    if not audience_data:
        logger.error("No valid user data found for Amazon")
        return False
    
    # Add users to the audience
    payload = {
        'users': audience_data
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 202:
        return True
    else:
        try:
            response_data = response.json()
            error_message = response_data.get('message', 'Unknown error')
        except:
            error_message = f"HTTP {response.status_code}"
        
        logger.error(f"Error adding users to Amazon audience: {error_message}")
        return False

def upload_to_amazon(audience_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload audience data to Amazon Advertising.
    
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
        
        # Get Amazon access token
        access_token = get_amazon_access_token(config)
        
        if not access_token:
            logger.error("Failed to get Amazon access token")
            return {"success": False, "error": "Failed to get Amazon access token"}
        
        # Get profile ID and region from config
        profile_id = config['amazon']['profile_id']
        region = config['amazon']['region']
        
        if not profile_id or not region:
            logger.error("Missing Amazon profile ID or region in config")
            return {"success": False, "error": "Missing Amazon profile ID or region in config"}
        
        # Get Amazon API headers
        headers = get_amazon_headers(access_token, profile_id, region)
        
        try:
            # Create a new audience
            audience_id = create_audience(
                audience_name=audience_name,
                audience_description=audience_description,
                headers=headers
            )
            
            if not audience_id:
                logger.error(f"Failed to create audience in Amazon: {audience_name}")
                return {"success": False, "error": "Failed to create audience"}
            
            # Add users to the audience
            success = add_users_to_audience(
                audience_id=audience_id,
                users=users,
                headers=headers
            )
            
            if success:
                logger.info(f"Successfully created audience in Amazon: {audience_name}")
                return {
                    "success": True,
                    "audience_id": audience_id
                }
            else:
                logger.error(f"Failed to add users to Amazon audience: {audience_name}")
                return {"success": False, "error": "Failed to add users to audience"}
        
        except Exception as e:
            error_message = f"Error creating audience in Amazon: {str(e)}"
            logger.exception(error_message)
            return {"success": False, "error": error_message}
    
    except Exception as e:
        logger.exception(f"Unhandled exception in upload_to_amazon: {str(e)}")
        return {"success": False, "error": str(e)}
