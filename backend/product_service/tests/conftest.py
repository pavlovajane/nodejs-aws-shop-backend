# tests/conftest.py
import os
import boto3
import pytest
from src.functions.mocks.products import products
from moto import mock_dynamodb

@pytest.fixture
def aws_credentials():
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

# Set environment variables for table names
os.environ['PRODUCTS_TABLE_NAME'] = 'products'
os.environ['STOCKS_TABLE_NAME'] = 'stocks'

@pytest.fixture
def mock_products():
    return products

@pytest.fixture
def api_gateway_event():
    def _event(path_parameters=None):
        return {
            "resource": "/products",
            "path": "/products",
            "httpMethod": "GET",
            "headers": {
                "Accept": "*/*",
                "Host": "api.example.com"
            },
            "pathParameters": path_parameters or None,
            "requestContext": {
                "resourceId": "123456",
                "apiId": "1234567890",
                "resourcePath": "/products",
                "httpMethod": "GET",
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                "accountId": "123456789012"
            }
        }
    return _event

@pytest.fixture
def lambda_context():
    """Generates a fake Lambda context object"""
    class LambdaContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "$LATEST"
            self.memory_limit_in_mb = 128
            self.aws_request_id = "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            self.log_group_name = "/aws/lambda/test-function"
            self.log_stream_name = "2020/01/01/[$LATEST]c6af9ac6-7b61-11e6-9a41-93e8deadbeef"

    return LambdaContext()

@pytest.fixture
def dynamodb_mock(mock_products, aws_credentials):
    with mock_dynamodb():
        # Initialize DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        # Create products table
        products_table = dynamodb.create_table(
            TableName='products',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create stocks table
        stocks_table = dynamodb.create_table(
            TableName='stocks',
            KeySchema=[{'AttributeName': 'product_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'product_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Wait for tables to become active
        products_table.meta.client.get_waiter('table_exists').wait(TableName='products')
        stocks_table.meta.client.get_waiter('table_exists').wait(TableName='stocks')

        # Insert mock data into products table
        products = mock_products
        for product in products:
            products_table.put_item(Item=product)

        # Insert mock data into stocks table
        stocks = [
            {"product_id": "7567ec4b-b10c-48c5-9345-fc73c48a80aa", "count": 5},
            {"product_id": "7567ec4b-b10c-48c5-9345-fc73c48a80a1", "count": 3},
        ]
        for stock in stocks:
            stocks_table.put_item(Item=stock)

        yield dynamodb
