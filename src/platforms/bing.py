import logging
from typing import Dict, Any, List
from datetime import datetime
from bingads.service_client import ServiceClient
from bingads.authorization import AuthorizationData, OAuthDesktopMobileAuthCodeGrant
from bingads.v13.bulk import BulkServiceManager
from bingads.v13.bulk.entities import BulkCustomerList
from bingads.v13.internal.bulk.entities.audience_criterions import BulkAudienceCriterion
from bingads.v13.internal.bulk.string_table import _StringTable

logger = logging.getLogger('audience_deployment.platforms.bing')

def get_bing_authorization(config: Dict[str, Any]) -> AuthorizationData:
    """
    Get Bing Ads authorization data.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        AuthorizationData: Bing Ads authorization data
    """
    client_id = config['bing']['client_id']
    client_secret = config['bing']['client_secret']
    developer_token = config['bing']['developer_token']
    refresh_token = config['bing']['refresh_token']
    account_id = config['bing']['account_id']
    
    # Set up OAuth authentication
    oauth = OAuthDesktopMobileAuthCodeGrant(client_id, client_secret)
    oauth.request_oauth_tokens_by_refresh_token(refresh_token)
    
    # Create authorization data
    authorization_data = AuthorizationData(
        account_id=account_id,
        customer_id=None,  # Will be set by the API
        developer_token=developer_token,
        authentication=oauth
    )
    
    return authorization_data

def create_customer_list(
    bulk_service: BulkServiceManager,
    authorization_data: AuthorizationData,
    audience_name: str,
    audience_description: str
) -> int:
    """
    Create a new Customer List in Bing Ads.
    
    Args:
        bulk_service (BulkServiceManager): Bing Ads Bulk Service Manager
        authorization_data (AuthorizationData): Bing Ads authorization data
        audience_name (str): Name of the audience
        audience_description (str): Description of the audience
        
    Returns:
        int: ID of the created customer list
    """
    # Create a new customer list
    customer_list = BulkCustomerList()
    customer_list.customer_list = {
        'Name': audience_name,
        'Description': audience_description,
        'MembershipLifeInDays': 10000,  # Default to long lifetime
        'Scope': 'Customer'  # Available to all accounts of the customer
    }
    
    # Upload the customer list
    upload_entities = [customer_list]
    
    bulk_service.upload_entities(
        authorization_data=authorization_data,
        entities=upload_entities
    )
    
    # Download the results to get the ID
    download_entities = bulk_service.download_entities(
        authorization_data=authorization_data,
        download_entities=['CustomerLists'],
        result_file_directory=None,
        result_file_name=None,
        overwrite_result_file=True,
        timeout_in_milliseconds=60000
    )
    
    # Find the customer list we just created
    for entity in download_entities:
        if isinstance(entity, BulkCustomerList) and entity.customer_list.Name == audience_name:
            return entity.customer_list.Id
    
    return None

def add_users_to_customer_list(
    bulk_service: BulkServiceManager,
    authorization_data: AuthorizationData,
    customer_list_id: int,
    users: List[Dict[str, Any]]
) -> bool:
    """
    Add users to a Bing Ads Customer List.
    
    Args:
        bulk_service (BulkServiceManager): Bing Ads Bulk Service Manager
        authorization_data (AuthorizationData): Bing Ads authorization data
        customer_list_id (int): ID of the customer list
        users (List[Dict[str, Any]]): List of user data dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Prepare user data for Bing Ads
    audience_data = []
    
    for user in users:
        user_data = {}
        
        if 'email' in user:
            user_data['Email'] = user['email']
        
        if 'phone' in user:
            user_data['Phone'] = user['phone']
        
        if 'address' in user:
            address = user['address']
            
            if 'first_name' in address:
                user_data['FirstName'] = address['first_name']
            
            if 'last_name' in address:
                user_data['LastName'] = address['last_name']
            
            if 'country_code' in address:
                user_data['Country'] = address['country_code']
            
            if 'postal_code' in address:
                user_data['PostalCode'] = address['postal_code']
        
        if user_data:
            audience_data.append(user_data)
    
    if not audience_data:
        logger.error("No valid user data found for Bing Ads")
        return False
    
    # Add users to the customer list
    try:
        # Get the CustomerListItemService
        service = ServiceClient(
            service='CustomerListItemService',
            version=13,
            authorization_data=authorization_data
        )
        
        # Add the audience data to the customer list
        response = service.AddCustomerListItems(
            CustomerListId=customer_list_id,
            CustomerListItems=audience_data
        )
        
        return True
    
    except Exception as e:
        logger.exception(f"Error adding users to Bing Ads customer list: {str(e)}")
        return False

def upload_to_bing(audience_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload audience data to Bing Ads.
    
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
        
        # Get Bing Ads authorization
        authorization_data = get_bing_authorization(config)
        
        # Create Bulk Service Manager
        bulk_service = BulkServiceManager(
            authorization_data=authorization_data,
            poll_interval_in_milliseconds=5000,
            environment='production'
        )
        
        try:
            # Create a new customer list
            customer_list_id = create_customer_list(
                bulk_service=bulk_service,
                authorization_data=authorization_data,
                audience_name=audience_name,
                audience_description=audience_description
            )
            
            if not customer_list_id:
                logger.error(f"Failed to create customer list in Bing Ads: {audience_name}")
                return {"success": False, "error": "Failed to create customer list"}
            
            # Add users to the customer list
            success = add_users_to_customer_list(
                bulk_service=bulk_service,
                authorization_data=authorization_data,
                customer_list_id=customer_list_id,
                users=users
            )
            
            if success:
                logger.info(f"Successfully created audience in Bing Ads: {audience_name}")
                return {
                    "success": True,
                    "customer_list_id": customer_list_id
                }
            else:
                logger.error(f"Failed to add users to Bing Ads customer list: {audience_name}")
                return {"success": False, "error": "Failed to add users to customer list"}
        
        except Exception as e:
            error_message = f"Error creating audience in Bing Ads: {str(e)}"
            logger.exception(error_message)
            return {"success": False, "error": error_message}
    
    except Exception as e:
        logger.exception(f"Unhandled exception in upload_to_bing: {str(e)}")
        return {"success": False, "error": str(e)}
