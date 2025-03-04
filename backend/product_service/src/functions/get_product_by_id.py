from decimal import Decimal
import json
import os
from typing import Dict, Any

import boto3

def get_product_by_id(products_table, product_id):
    response = products_table.get_item(Key={'id': product_id})
    item = response.get('Item')
    return item

def get_stock_by_product_id(stocks_table, product_id):
    response = stocks_table.get_item(Key={'product_id': product_id})
    item = response.get('Item')
    return item    

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to create standardized response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Content-Type": "application/json"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }

def handler(event: Dict[str, Any], context: Any, dynamodb = None) -> Dict[str, Any]:
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

        dynamodb = boto3.resource('dynamodb') if not dynamodb else dynamodb
        products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
        stocks_table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])

        # Find the product
        product = get_product_by_id(products_table, product_id)
        
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
        print(f"Fetched products: {product}")

        stock = get_stock_by_product_id(stocks_table, product_id)
        stock_count = stock.get('count', 0) if stock else 0
        
        output_product = {
            'id': product_id,
            'title': product['title'],
            'description': product['description'],
            'price': float(product['price']),
            'count': int(stock_count)
        }

        # Return the product if found
        return create_response(200, {
            "data": output_product,
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
