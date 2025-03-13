import json
from typing import Any, Dict
import boto3
import os

# Initialize S3 client
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']
UPLOAD_FOLDER = 'uploaded'

def handler(event, context: Any):
    """
    Lambda function generates a signed URL for uploading CSV files to S3
    Parameters: 'name'  in query string
    Returns: a signed URL as a string
    """
    print(f"Incoming request: {json.dumps(event)}")

    try:
        # Get filename from query parameters
        query_parameters = event.get('queryStringParameters', {})
        if not query_parameters or 'name' not in query_parameters:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                },
                "body": json.dumps({
                    "message": "Missing required query parameter: name"
                })
            }

        file_name = query_parameters['name']

        # Validate file extension
        if not file_name.endswith('.csv'):
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                },
                "body": json.dumps({
                    "message": "Invalid file format. Only CSV files are allowed."
                })
            }

        # Generate pre-signed URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': BUCKET_NAME,
                    'Key': f"{UPLOAD_FOLDER}/{file_name}",
                    'ContentType': 'text/csv'
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",  # Enable CORS for frontend integration
                    "Access-Control-Allow-Credentials": True
                },
                "body": presigned_url  
            }

        except Exception as e:
            print(f"Error generating pre-signed URL: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                },
                "body": json.dumps({
                    "message": "Error generating pre-signed URL"
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
                "message": "Internal server error"
            })
        }
