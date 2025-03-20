# tests/test_import_file_parser.py
import os
import unittest
from unittest.mock import patch, MagicMock
import json

os.environ.clear()
os.environ.update({
    'BUCKET_NAME': 'test-bucket',
    'PRODUCTS_TABLE_NAME': 'test-products-table',
    'STOCKS_TABLE_NAME': 'test-stocks-table'
})

from backend.product_service.tests.test_catalog_batch_process import mock_aws_clients
from src.functions.import_file_parser import handler

class TestImportFileParser(unittest.TestCase):
    def setUp(self):
        print("\nVerifying environment variables:")
        print(f"BUCKET_NAME: {os.environ.get('BUCKET_NAME')}")
        print(f"PRODUCTS_TABLE_NAME: {os.environ.get('PRODUCTS_TABLE_NAME')}")
        print(f"STOCKS_TABLE_NAME: {os.environ.get('STOCKS_TABLE_NAME')}")

    @patch('src.functions.import_file_parser.s3_client')
    @patch('src.functions.import_file_parser.dynamodb')
    def test_successful_file_processing(self, mock_dynamodb, mock_s3):
        try:
            # Mock CSV content with proper headers and data
            csv_content = 'Title,Description,Price,Count\nTest Product,Test Description,10.00,5'
            
            # Mock S3 response
            mock_body = MagicMock()
            mock_body.read.return_value = csv_content.encode('utf-8')
            mock_s3.get_object.return_value = {
                'Body': mock_body
            }

            # Mock DynamoDB transact_write_items
            mock_dynamodb.transact_write_items.return_value = {
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }

            # Mock S3 operations
            mock_s3.copy_object.return_value = {
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }
            mock_s3.delete_object.return_value = {
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }

            event = {
                "Records": [{
                    "s3": {
                        "bucket": {
                            "name": "test-bucket"
                        },
                        "object": {
                            "key": "uploaded/test.csv"
                        }
                    }
                }]
            }

            print("\nTest Configuration:")
            print(f"Event: {json.dumps(event)}")
            
            response = handler(event, None)
            
            print(f"Response: {json.dumps(response)}")
            if response['statusCode'] == 500:
                print(f"Error message: {response.get('body', 'No error message')}")

            self.assertEqual(response['statusCode'], 200)
            
            # Verify S3 operations
            mock_s3.get_object.assert_called_once_with(
                Bucket='test-bucket',
                Key='uploaded/test.csv'
            )
            
            # Verify SQS send_message was called
            mock_aws_clients['sqs'].send_message.assert_called_once()
            call_args = mock_aws_clients['sqs'].send_message.call_args[1]
            message_body = json.loads(call_args['MessageBody'])
            
            assert message_body == {
                'Title': 'Test Product',
                'Description': 'Test Description',
                'Price': '100',
                'Count': '5'
            }
            
            # Verify file movement
            mock_s3.copy_object.assert_called_once()
            mock_s3.delete_object.assert_called_once()

            print("\nMock Calls:")
            print(f"get_object calls: {mock_s3.get_object.mock_calls}")
            print(f"DynamoDB transact_write_items calls: {mock_dynamodb.transact_write_items.mock_calls}")
            print(f"copy_object calls: {mock_s3.copy_object.mock_calls}")
            print(f"delete_object calls: {mock_s3.delete_object.mock_calls}")

        except Exception as e:
            print(f"\nTest failed with exception: {str(e)}")
            raise

    def tearDown(self):
        os.environ.clear()

if __name__ == '__main__':
    unittest.main()
