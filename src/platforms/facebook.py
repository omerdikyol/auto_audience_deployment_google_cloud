import logging
from typing import Dict, Any, List
from datetime import datetime
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.adaccount import AdAccount

logger = logging.getLogger('audience_deployment.platforms.facebook')

def initialize_facebook_api(config: Dict[str, Any]) -> None:
    """
    Initialize the Facebook Marketing API.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
    """
    app_id = config['facebook']['app_id']
    app_secret = config['facebook']['app_secret']
    access_token = config['facebook']['access_token']
    
    FacebookAdsApi.init(app_id, app_secret, access_token)

def create_custom_audience(
    account_id: str,
    audience_name: str,
    audience_description: str
) -> CustomAudience:
    """
    Create a new Custom Audience in Facebook.
    
    Args:
        account_id (str): Facebook Ad Account ID
        audience_name (str): Name of the audience
        audience_description (str): Description of the audience
        
    Returns:
        CustomAudience: The created Custom Audience object
    """
    # Format account ID with 'act_' prefix if not already present
    if not account_id.startswith('act_'):
        account_id = f'act_{account_id}'
    
    # Get the Ad Account
    ad_account = AdAccount(account_id)
    
    # Create the Custom Audience
    audience = ad_account.create_custom_audience(
        params={
            'name': audience_name,
            'description': audience_description,
            'customer_file_source': 'USER_PROVIDED_ONLY',
        }
    )
    
    return audience

def add_users_to_custom_audience(
    audience: CustomAudience,
    users: List[Dict[str, Any]]
) -> bool:
    """
    Add users to a Facebook Custom Audience.
    
    Args:
        audience (CustomAudience): The Custom Audience object
        users (List[Dict[str, Any]]): List of user data dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare user data for Facebook
    schema = []
    user_data = []
    
    # Determine schema based on first user
    if users and 'email' in users[0]:
        schema.append('EMAIL')
    if users and 'phone' in users[0]:
        schema.append('PHONE')
    if users and 'address' in users[0] and 'first_name' in users[0]['address'] and 'last_name' in users[0]['address']:
        schema.extend(['FN', 'LN'])
        if 'zip' in users[0]['address']:
            schema.append('ZIP')
        if 'country_code' in users[0]['address']:
            schema.append('COUNTRY')
    
    # No valid schema found
    if not schema:
        logger.error("No valid schema could be determined from user data")
        return False
    
    # Prepare user data
    for user in users:
        user_row = []
        
        if 'EMAIL' in schema and 'email' in user:
            user_row.append(user['email'])
        elif 'EMAIL' in schema:
            user_row.append('')
            
        if 'PHONE' in schema and 'phone' in user:
            user_row.append(user['phone'])
        elif 'PHONE' in schema:
            user_row.append('')
            
        if 'FN' in schema and 'address' in user and 'first_name' in user['address']:
            user_row.append(user['address']['first_name'])
        elif 'FN' in schema:
            user_row.append('')
            
        if 'LN' in schema and 'address' in user and 'last_name' in user['address']:
            user_row.append(user['address']['last_name'])
        elif 'LN' in schema:
            user_row.append('')
            
        if 'ZIP' in schema and 'address' in user and 'zip' in user['address']:
            user_row.append(user['address']['zip'])
        elif 'ZIP' in schema:
            user_row.append('')
            
        if 'COUNTRY' in schema and 'address' in user and 'country_code' in user['address']:
            user_row.append(user['address']['country_code'])
        elif 'COUNTRY' in schema:
            user_row.append('')
        
        if user_row:
            user_data.append(user_row)
    
    # Add users to the audience
    if user_data:
        audience.add_users(
            schema=schema,
            data=user_data,
            is_hashed=True  # Assuming data is already hashed
        )
        return True
    
    return False

def upload_to_facebook(audience_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload audience data to Facebook.
    
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
        
        # Initialize Facebook API
        initialize_facebook_api(config)
        
        # Get account ID from config
        account_id = config['facebook']['account_id']
        
        if not account_id:
            logger.error("No Facebook account ID found in config")
            return {"success": False, "error": "No Facebook account ID found in config"}
        
        try:
            # Create a new Custom Audience
            audience = create_custom_audience(
                account_id=account_id,
                audience_name=audience_name,
                audience_description=audience_description
            )
            
            # Add users to the audience
            success = add_users_to_custom_audience(
                audience=audience,
                users=users
            )
            
            if success:
                logger.info(f"Successfully created audience in Facebook: {audience_name}")
                return {
                    "success": True,
                    "audience_id": audience['id']
                }
            else:
                logger.error(f"Failed to add users to Facebook audience: {audience_name}")
                return {"success": False, "error": "Failed to add users to audience"}
        
        except Exception as e:
            error_message = f"Error creating audience in Facebook: {str(e)}"
            logger.exception(error_message)
            return {"success": False, "error": error_message}
    
    except Exception as e:
        logger.exception(f"Unhandled exception in upload_to_facebook: {str(e)}")
        return {"success": False, "error": str(e)}
