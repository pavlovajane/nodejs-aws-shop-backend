# src/functions/catalog_batch_process.py
import json
import os
import uuid
import boto3
from typing import Dict, Any
    
dynamodb = boto3.client('dynamodb')
products_table = os.environ['PRODUCTS_TABLE_NAME']
stocks_table = os.environ['STOCKS_TABLE_NAME']

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
    
def write_to_dynamo(requests):
    dynamodb.transact_write_items(
        TransactItems=requests
    )

def handler(event, context: Any):
    sns_client = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    
    try:
        requests = []
        for record in event['Records']:
            message_body = json.loads(record['body'])
            to_dynamo_request(message_body, requests)

        # create products
        write_to_dynamo(requests)
        
        # Send notification to SNS
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject='Products Created Successfully',
            Message=f'Successfully processed and created {len(event["Records"])} products'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Products created successfully')
        }
    
    except Exception as e:
        print(f"Error processing messages: {str(e)}")
        raise e
