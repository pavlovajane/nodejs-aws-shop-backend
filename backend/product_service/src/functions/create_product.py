import json
from typing import Any, Dict
import boto3
import os
import uuid
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

# Initialize DynamoDB resource
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

def to_dynamo_request(parsed, requests):
    product_id = str(uuid.uuid4())
    title = parsed['Title']
    description = parsed['Description']
    price = parsed['Price']
    count = parsed['Count']
    new_product = {
        'id': {
            'S': product_id,
        },
        'title': {
            'S': title,
        },
        'description': {
            'S': description,
        },
        'price': {
            'N': price
        },
    }
    requests.append({
        'Put': {
            'TableName': products_table,
            'Item': new_product
        }
    })
    new_stock = {
        'product_id': {
            'S': product_id,
        },
        'count': {
            'N': count,
        },
    }
    requests.append({
        'Put': {
            'TableName': stocks_table,
            'Item': new_stock
        }
    })
    
def write_to_dynamo(requests, dynamodb):
    dynamodb.transact_write_items(
        TransactItems=requests
    )

def handler(event, context : Any, dynamodb = None):
    
    dynamodb = boto3.client('dynamodb') if not dynamodb else dynamodb
    products_table = os.environ['PRODUCTS_TABLE_NAME']
    stocks_table = os.environ['STOCKS_TABLE_NAME']

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
        requests = []
        title = body['title']
        description = body['description']
        price = body['price']
        count = body['count']
        new_product = {
            'id': {
                'S': product_id,
            },
            'title': {
                'S': title,
            },
            'description': {
                'S': description,
            },
            'price': {
                'N': str(price)
            },
        }
        requests.append({
            'Put': {
                'TableName': products_table,
                'Item': new_product
            }
        })
        new_stock = {
            'product_id': {
                'S': product_id,
            },
            'count': {
                'N': str(count),
            },
        }
        requests.append({
            'Put': {
                'TableName': stocks_table,
                'Item': new_stock
            }
        })
        # Perform a transaction to ensure both product and stock are created together
        try:
            write_to_dynamo(requests, dynamodb=dynamodb)
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
