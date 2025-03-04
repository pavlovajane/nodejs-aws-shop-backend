import json
from typing import Any
import boto3
import os
import uuid
from decimal import Decimal

from backend.product_service.src.functions.get_product_by_id import DecimalEncoder

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
stocks_table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])

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

def handler(event, context : Any, dynamodb = None):
    print(f"Incoming request: {json.dumps(event)}")

    try:
        body = json.loads(event['body'])

        # Validate required fields
        required_fields = ['title', 'description', 'price', 'count']
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': f"Missing required fields: {', '.join(missing_fields)}"})
            }

        product_id = str(uuid.uuid4())

        new_product = {
            'id': product_id,
            'title': body['title'],
            'description': body['description'],
            'price': Decimal(str(body['price']))
        }

        new_stock = {
            'product_id': product_id,
            'count': int(body['count'])
        }

        # Perform a transaction to ensure both product and stock are created together
        try:
            dynamodb.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': products_table,
                            'Item': new_product
                        }
                    },
                    {
                        'Put': {
                            'TableName': stocks_table,
                            'Item': new_stock
                        }
                    }
                ]
            )
            print(f"Transaction successful: Product {new_product} and Stock {new_stock} created")
        except Exception as e:
            print(f"Transaction failed: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Transaction failed', 'error': str(e)})
            }

        response_body = {
            'message': 'Product and stock created successfully',
            'product': new_product,
            'stock': new_stock
        }

        return {
            'statusCode': 201,
            'body': json.dumps(response_body, default=str)
        }

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
