import json
import logging
from typing import Dict, Any, Optional
from google.cloud import storage

logger = logging.getLogger('audience_deployment.storage')

def download_audience_data(file_path: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Download audience data from Google Cloud Storage.
    
    Args:
        file_path (str): Path to the JSON file in GCS
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Optional[Dict[str, Any]]: Audience data as a dictionary, or None if download fails
    """
    try:
        # Get bucket name from config
        bucket_name = config['gcp']['bucket_name']
        
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        # Download the file as a string
        json_string = blob.download_as_text()
        
        # Parse JSON
        audience_data = json.loads(json_string)
        
        logger.info(f"Successfully downloaded audience data from gs://{bucket_name}/{file_path}")
        return audience_data
    
    except Exception as e:
        logger.exception(f"Error downloading audience data from gs://{bucket_name}/{file_path}: {str(e)}")
        return None
