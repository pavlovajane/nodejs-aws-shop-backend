import os
import json
import base64
from typing import Dict, Any

def get_user_credentials() -> Dict[str, str]:    
    credentials = {}
    for key, value in os.environ.items():
        if '=' in value:
            parts = value.split('=')
            if len(parts) == 2:
                username, password = parts
                credentials[username] = password
    return credentials

def decode_token(auth_token: str) -> tuple:
    
    try:
        # Remove 'Basic ' prefix and decode
        encoded_credentials = auth_token.split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':')
        return username, password
    except Exception:
        return None, None

def generate_policy(principal_id: str, effect: str, resource: str) -> Dict[str, Any]:
    
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    
    # Extract the Authorization header
    auth_header = event.get('headers', {}).get('Authorization')
    
    # Check if Authorization header exists
    if not auth_header:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized'})
        }

    # Decode credentials from the Authorization header
    username, password = decode_token(auth_header)
    print(username, password)
    if not username or not password:
        return {
            'statusCode': 403,
            'body': json.dumps({'message': 'Forbidden'})
        }

    # Get credentials from environment variables
    valid_credentials = get_user_credentials()
    print(valid_credentials)
    # Verify credentials
    if username in valid_credentials and valid_credentials[username] == password:
        # Generate policy for successful authorization
        method_arn = event['methodArn']
        return generate_policy(username, 'Allow', method_arn)
    
    return {
        'statusCode': 403,
        'body': json.dumps({'message': 'Forbidden'})
    }
