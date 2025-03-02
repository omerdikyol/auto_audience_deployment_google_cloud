import json
from typing import Dict, Any, Callable
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
