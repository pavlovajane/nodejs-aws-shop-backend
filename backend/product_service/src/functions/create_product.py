import json
from typing import Any
import boto3
import os
import uuid
from decimal import Decimal

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
stocks_table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])

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

        # Put product and stock items into DynamoDB
        products_table.put_item(Item=new_product)
        print(f"Product created: {new_product}")

        stocks_table.put_item(Item=new_stock)
        print(f"Stock created: {new_stock}")

        response_body = {
            'message': 'Product and stock created successfully',
            'product': new_product,
            'stock': new_stock
        }

        return {
            'statusCode': 201,
            'body': json.dumps(response_body, default=str)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
