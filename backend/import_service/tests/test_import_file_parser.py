# tests/test_import_file_parser.py
import unittest
from unittest.mock import patch, MagicMock
from src.functions.import_file_parser import handler

class TestImportFileParser(unittest.TestCase):
    @patch('src.functions.import_file_parser.s3_client')
    def test_successful_file_processing(self, mock_s3):
        mock_response = {
            'Body': MagicMock()
        }
        mock_response['Body'].read.return_value = b'header1,header2\nvalue1,value2'
        mock_s3.get_object.return_value = mock_response

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

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        mock_s3.get_object.assert_called_once()
        mock_s3.copy_object.assert_called_once()
        mock_s3.delete_object.assert_called_once()

    @patch('src.functions.import_file_parser.s3_client')
    def test_error_handling_invalid_csv(self, mock_s3):
        mock_s3.get_object.side_effect = Exception("S3 Error")
        
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

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn("Error processing files", response['body'])
