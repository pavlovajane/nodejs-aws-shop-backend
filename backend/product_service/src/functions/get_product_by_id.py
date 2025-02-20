import json
from typing import Dict, Any
from .mocks.products import products

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to create standardized response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        # Check if pathParameters exists and contains productId
        if not event.get('pathParameters') or 'productId' not in event['pathParameters']:
            return create_response(400, {
                "message": "Bad Request: Missing productId parameter"
            })

        product_id = event['pathParameters']['productId']
        
        # Validate productId is not empty
        if not product_id:
            return create_response(400, {
                "message": "Bad Request: ProductId cannot be empty"
            })

        # Find the product
        product = next(
            (item for item in products if item["id"] == product_id),
            None
        )
        
        # Return 404 if product not found
        if not product:
            return create_response(404, {
                "message": "Product not found",
                "statusCode": 404,
                "error": {
                    "code": "PRODUCT_NOT_FOUND",
                    "productId": product_id
                }
            })
        
        # Return the product if found
        return create_response(200, {
            "data": product,
            "statusCode": 200
        })
        
    except Exception as error:
        print(f"Error: {str(error)}")  # Basic error logging
        return create_response(500, {
            "message": "Internal server error",
            "statusCode": 500,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "details": str(error) if isinstance(error, Exception) else "Unknown error"
            }
        })
