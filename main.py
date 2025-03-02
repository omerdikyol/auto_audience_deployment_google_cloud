import json
import os
import logging
import functions_framework
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import modules from our project
from src.storage.gcs import download_audience_data
from src.platforms.google_ads import upload_to_google_ads
from src.platforms.facebook import upload_to_facebook
from src.platforms.bing import upload_to_bing
from src.platforms.tiktok import upload_to_tiktok
from src.platforms.amazon import upload_to_amazon
from src.sheets.audience_library import update_audience_library
from src.utils.config import load_config
from src.utils.logging_setup import setup_logging

# Setup logging
logger = setup_logging()

@functions_framework.http
def process_audience(request):
    """
    HTTP Cloud Function to process audience data from GCS and upload to ad platforms.
    
    Args:
        request (flask.Request): The request object.
        
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`.
    """
    try:
        # Parse request data
        request_json = request.get_json(silent=True)
        
        if not request_json:
            logger.error("No JSON data in request")
            return {"success": False, "error": "No JSON data in request"}, 400
        
        # Load configuration
        config = load_config()
        
        # Extract parameters from request
        gcs_file_path = request_json.get('gcs_file_path')
        platforms = request_json.get('platforms', [])
        
        if not gcs_file_path:
            logger.error("Missing required parameter: gcs_file_path")
            return {"success": False, "error": "Missing required parameter: gcs_file_path"}, 400
        
        if not platforms:
            logger.error("Missing required parameter: platforms")
            return {"success": False, "error": "Missing required parameter: platforms"}, 400
        
        # Download audience data from GCS
        logger.info(f"Downloading audience data from {gcs_file_path}")
        audience_data = download_audience_data(gcs_file_path, config)
        
        if not audience_data:
            logger.error(f"Failed to download audience data from {gcs_file_path}")
            return {"success": False, "error": f"Failed to download audience data from {gcs_file_path}"}, 500
        
        # Process each platform
        results = {}
        audience_name = audience_data.get('name', 'Unknown Audience')
        
        for platform in platforms:
            try:
                logger.info(f"Processing platform: {platform}")
                
                if platform.lower() == 'google_ads':
                    result = upload_to_google_ads(audience_data, config)
                elif platform.lower() == 'facebook':
                    result = upload_to_facebook(audience_data, config)
                elif platform.lower() == 'bing':
                    result = upload_to_bing(audience_data, config)
                elif platform.lower() == 'tiktok':
                    result = upload_to_tiktok(audience_data, config)
                elif platform.lower() == 'amazon':
                    result = upload_to_amazon(audience_data, config)
                else:
                    logger.warning(f"Unsupported platform: {platform}")
                    results[platform] = {"success": False, "error": f"Unsupported platform: {platform}"}
                    continue
                
                results[platform] = result
                
                # Update audience library in Google Sheets if upload was successful
                if result.get('success'):
                    update_audience_library(
                        platform=platform,
                        audience_name=audience_name,
                        created_date=datetime.now().strftime('%Y-%m-%d'),
                        config=config
                    )
            except Exception as e:
                logger.exception(f"Error processing platform {platform}: {str(e)}")
                results[platform] = {"success": False, "error": str(e)}
        
        # Determine overall success
        overall_success = any(result.get('success', False) for result in results.values())
        
        return {
            "success": overall_success,
            "results": results,
            "audience_name": audience_name,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.exception(f"Unhandled exception in process_audience: {str(e)}")
        return {"success": False, "error": str(e)}, 500

if __name__ == "__main__":
    # For local testing only
    from src.utils.local_testing import simulate_http_request
    
    # Example request data
    request_data = {
        "gcs_file_path": "audiences/test_audience.json",
        "platforms": ["google_ads", "facebook"]
    }
    
    response = simulate_http_request(process_audience, request_data)
    print(json.dumps(response, indent=2))
