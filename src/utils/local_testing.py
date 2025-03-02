import json
from typing import Dict, Any, Callable, Optional
from flask import Request

class MockRequest:
    """Mock Flask request object for local testing."""
    
    def __init__(self, json_data: Dict[str, Any]):
        self.json_data = json_data
    
    def get_json(self, silent=False):
        return self.json_data

def simulate_http_request(function: Callable, json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate an HTTP request to a Cloud Function.
    
    Args:
        function (Callable): The Cloud Function to call
        json_data (Dict[str, Any]): JSON data to pass in the request
        
    Returns:
        Dict[str, Any]: The response from the function
    """
    mock_request = MockRequest(json_data)
    response = function(mock_request)
    
    # Cloud Functions can return a tuple (response, status_code)
    if isinstance(response, tuple):
        return response[0]
    
    return response


class MockCloudEvent:
    """Mock CloudEvent object for local testing."""
    
    def __init__(self, event_type: str, source: str, data: Dict[str, Any]):
        self.type = event_type
        self.source = source
        self.data = data
        self.attributes = {
            "type": event_type,
            "source": source
        }


def simulate_gcs_trigger(function: Callable, bucket: str, file_path: str) -> None:
    """
    Simulate a GCS trigger event to a Cloud Function.
    
    Args:
        function (Callable): The Cloud Function to call
        bucket (str): The GCS bucket name
        file_path (str): The file path within the bucket
        
    Returns:
        None: Cloud Functions triggered by GCS events don't return values
    """
    event_type = "google.cloud.storage.object.v1.finalized"
    source = f"//storage.googleapis.com/projects/_/buckets/{bucket}"
    data = {
        "bucket": bucket,
        "name": file_path,
        "contentType": "application/json"
    }
    
    mock_event = MockCloudEvent(event_type, source, data)
    function(mock_event)
    
    return None
