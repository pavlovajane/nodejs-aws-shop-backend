# tests/test_catalog_batch_process.py
import pytest
import json
import os
import uuid
from src.functions.catalog_batch_process import handler

@pytest.fixture
def sqs_event():
    return {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": json.dumps({
                    "Title": "Test Product",
                    "Description": "Test Description",
                    "Price": "100",
                    "Count": "5"
                }),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:region:123456789012:MyQueue",
                "awsRegion": "us-east-1"
            }
        ]
    }

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv('SNS_TOPIC_ARN', 'arn:aws:sns:region:123456789012:MyTopic')
    monkeypatch.setenv('PRODUCTS_TABLE_NAME', 'products-table')
    monkeypatch.setenv('STOCKS_TABLE_NAME', 'stocks-table')

@pytest.fixture
def mock_aws_clients(mocker):
    # Create mock clients
    mock_dynamodb = mocker.Mock()
    mock_sns = mocker.Mock()
    
    # Set up boto3 mock
    mock_boto3 = mocker.patch('boto3.client')
    mock_boto3.side_effect = lambda service: {
        'dynamodb': mock_dynamodb,
        'sns': mock_sns
    }[service]
    
    # Mock UUID
    mocker.patch('uuid.uuid4', return_value='mocked-uuid')
    
    return {
        'dynamodb': mock_dynamodb,
        'sns': mock_sns
    }

def test_successful_processing(sqs_event, mock_aws_clients):
    # Call the handler
    response = handler(sqs_event, None)

    expected_transact_items = [
        {
            'Put': {
                'TableName': 'products-table',
                'Item': {
                    'id': {'S': 'mocked-uuid'},
                    'title': {'S': 'Test Product'},
                    'description': {'S': 'Test Description'},
                    'price': {'N': '100'}
                }
            }
        },
        {
            'Put': {
                'TableName': 'stocks-table',
                'Item': {
                    'product_id': {'S': 'mocked-uuid'},
                    'count': {'N': '5'}
                }
            }
        }
    ]

    # Verify DynamoDB call
    mock_aws_clients['dynamodb'].transact_write_items.assert_called_once_with(
        TransactItems=expected_transact_items
    )
    
    # Verify SNS call
    mock_aws_clients['sns'].publish.assert_called_once_with(
        TopicArn='arn:aws:sns:region:123456789012:MyTopic',
        Subject='Products Created Successfully',
        Message='Successfully processed and created 1 products'
    )

    # Verify response
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'Products created successfully'

def test_processing_error(sqs_event, mock_aws_clients):
    # Configure DynamoDB mock to raise an exception
    mock_aws_clients['dynamodb'].transact_write_items.side_effect = Exception('Database error')

    # Test that the handler raises an exception
    with pytest.raises(Exception) as exc_info:
        handler(sqs_event, None)
    
    assert str(exc_info.value) == 'Database error'
