import logging
from typing import Dict, Any, List
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger('audience_deployment.platforms.google_ads')

def get_google_ads_client(config: Dict[str, Any]) -> GoogleAdsClient:
    """
    Get authenticated Google Ads API client.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        GoogleAdsClient: Authenticated Google Ads client
    """
    # Extract credentials from config
    credentials = {
        "client_id": config['google_ads']['client_id'],
        "client_secret": config['google_ads']['client_secret'],
        "refresh_token": config['google_ads']['refresh_token'],
        "developer_token": config['google_ads']['developer_token'],
        "login_customer_id": config['google_ads']['login_customer_id'],
        "use_proto_plus": True
    }
    
    # Create and return the client
    return GoogleAdsClient.load_from_dict(credentials)

def create_customer_match_user_list(
    client: GoogleAdsClient,
    customer_id: str,
    audience_name: str,
    audience_description: str,
    membership_life_span: int = 10000
) -> str:
    """
    Create a new Customer Match user list.
    
    Args:
        client (GoogleAdsClient): Google Ads client
        customer_id (str): Google Ads customer ID
        audience_name (str): Name of the audience
        audience_description (str): Description of the audience
        membership_life_span (int, optional): Membership life span in days. Defaults to 10000.
        
    Returns:
        str: Resource name of the created user list
    """
    # Get the UserListService
    user_list_service = client.get_service("UserListService")
    
    # Create a Customer Match user list
    user_list_operation = client.get_type("UserListOperation")
    user_list = user_list_operation.create
    
    # Set basic list info
    user_list.name = audience_name
    user_list.description = audience_description
    user_list.membership_life_span = membership_life_span
    
    # Set the list type to CRM_BASED
    user_list.crm_based_user_list.upload_key_type = client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
    
    # Add the user list
    response = user_list_service.mutate_user_lists(
        customer_id=customer_id,
        operations=[user_list_operation]
    )
    
    # Return the resource name of the created list
    return response.results[0].resource_name

def add_users_to_customer_match_list(
    client: GoogleAdsClient,
    customer_id: str,
    user_list_resource_name: str,
    user_data: List[Dict[str, Any]]
) -> bool:
    """
    Add users to a Customer Match user list.
    
    Args:
        client (GoogleAdsClient): Google Ads client
        customer_id (str): Google Ads customer ID
        user_list_resource_name (str): Resource name of the user list
        user_data (List[Dict[str, Any]]): List of user data dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get the OfflineUserDataJobService
    offline_user_data_job_service = client.get_service("OfflineUserDataJobService")
    
    # Create an offline user data job for adding users to the list
    offline_user_data_job = client.get_type("OfflineUserDataJob")
    offline_user_data_job.type_ = client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
    offline_user_data_job.customer_match_user_list_metadata.user_list = user_list_resource_name
    
    # Create the job
    create_job_response = offline_user_data_job_service.create_offline_user_data_job(
        customer_id=customer_id,
        job=offline_user_data_job
    )
    
    job_resource_name = create_job_response.resource_name
    
    # Create user data operations for each user
    operations = []
    
    for user in user_data:
        operation = client.get_type("OfflineUserDataJobOperation")
        user_data_entry = operation.create
        
        # Add user identifiers based on available data
        if 'email' in user:
            user_identifier = client.get_type("UserIdentifier")
            user_identifier.hashed_email = user['email']
            user_data_entry.user_identifiers.append(user_identifier)
        
        if 'phone' in user:
            user_identifier = client.get_type("UserIdentifier")
            user_identifier.hashed_phone_number = user['phone']
            user_data_entry.user_identifiers.append(user_identifier)
            
        if 'address' in user:
            user_identifier = client.get_type("UserIdentifier")
            address_info = client.get_type("OfflineUserAddressInfo")
            address = user['address']
            
            if 'first_name' in address:
                address_info.hashed_first_name = address['first_name']
            if 'last_name' in address:
                address_info.hashed_last_name = address['last_name']
            if 'country_code' in address:
                address_info.country_code = address['country_code']
            if 'postal_code' in address:
                address_info.postal_code = address['postal_code']
                
            user_identifier.address_info = address_info
            user_data_entry.user_identifiers.append(user_identifier)
            
        if user_data_entry.user_identifiers:
            operations.append(operation)
    
    # Add the operations to the job
    if operations:
        offline_user_data_job_service.add_offline_user_data_job_operations(
            resource_name=job_resource_name,
            operations=operations
        )
        
        # Run the job
        offline_user_data_job_service.run_offline_user_data_job(
            resource_name=job_resource_name
        )
        
        return True
    
    return False

def upload_to_google_ads(audience_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload audience data to Google Ads.
    
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
        
        # Get Google Ads client
        client = get_google_ads_client(config)
        
        # Get customer IDs from config
        customer_ids = config['google_ads']['customer_ids']
        
        if not customer_ids:
            logger.error("No customer IDs found in config")
            return {"success": False, "error": "No customer IDs found in config"}
        
        results = {}
        
        # Process each customer ID
        for customer_id in customer_ids:
            try:
                # Create a new user list
                user_list_resource_name = create_customer_match_user_list(
                    client=client,
                    customer_id=customer_id,
                    audience_name=audience_name,
                    audience_description=audience_description
                )
                
                # Add users to the list
                success = add_users_to_customer_match_list(
                    client=client,
                    customer_id=customer_id,
                    user_list_resource_name=user_list_resource_name,
                    user_data=users
                )
                
                results[customer_id] = {
                    "success": success,
                    "user_list_resource_name": user_list_resource_name if success else None
                }
                
                logger.info(f"Successfully created audience in Google Ads account {customer_id}: {audience_name}")
            
            except GoogleAdsException as e:
                error_message = f"Google Ads API error: {e.error.message}"
                logger.exception(error_message)
                results[customer_id] = {"success": False, "error": error_message}
            
            except Exception as e:
                error_message = f"Error creating audience in Google Ads account {customer_id}: {str(e)}"
                logger.exception(error_message)
                results[customer_id] = {"success": False, "error": error_message}
        
        # Determine overall success
        overall_success = any(result.get('success', False) for result in results.values())
        
        return {
            "success": overall_success,
            "results": results
        }
    
    except Exception as e:
        logger.exception(f"Unhandled exception in upload_to_google_ads: {str(e)}")
        return {"success": False, "error": str(e)}
