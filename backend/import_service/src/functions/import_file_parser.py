from decimal import Decimal
import json
import os
import boto3
import csv
import io
from typing import Any
import uuid

# Initialize S3 client
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

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
    
    print(f"Incoming S3 event: {json.dumps(event)}")

    try:
        # Get bucket and key from the S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            print(f"Processing file: {key} from bucket: {bucket}")

            # Get the object from S3
            try:
                response = s3_client.get_object(Bucket=bucket, Key=key)
                # Create a stream from the S3 object body
                file_content = response['Body'].read().decode('utf-8')
                csv_stream = io.StringIO(file_content)

                # Parse CSV
                csv_reader = csv.DictReader(csv_stream)
                
                # dynamo requests
                requests = []
                
                # Process each row
                for row in csv_reader:
                    print(f"Parsed record: {json.dumps(row)}")
                    to_dynamo_request(row, requests)

                # write to dynamo
                write_to_dynamo(requests)

                # After successful processing, copy to parsed folder and delete from uploaded
                try:
                    # Copy to parsed folder
                    new_key = key.replace('uploaded/', 'parsed/')
                    s3_client.copy_object(
                        Bucket=bucket,
                        CopySource={'Bucket': bucket, 'Key': key},
                        Key=new_key
                    )

                    # Delete from uploaded folder
                    s3_client.delete_object(
                        Bucket=bucket,
                        Key=key
                    )

                    print(f"File processed and moved to: {new_key}")

                except Exception as move_error:
                    print(f"Error moving file: {str(move_error)}")
                    raise move_error

            except Exception as e:
                print(f"Error processing file {key}: {str(e)}")
                raise e

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({
                "message": "Files processed successfully"
            })
        }

    except Exception as error:
        print(f"Error: {str(error)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({
                "message": "Error processing files"
            })
        }
