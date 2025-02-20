import json
from typing import Dict, Any
from .mocks.products import products

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Enable CORS for frontend integration
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps(products)
        }
    except Exception as error:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({"message": "Internal server error"})
        }
