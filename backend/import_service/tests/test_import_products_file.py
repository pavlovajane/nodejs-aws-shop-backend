
import unittest
from unittest.mock import patch, MagicMock
from src.functions.import_products_file import handler

class TestImportProductsFile(unittest.TestCase):
    @patch('src.functions.import_products_file.s3_client')
    def test_successful_url_generation(self, mock_s3):
        mock_s3.generate_presigned_url.return_value = "https://test-url.com"
        event = {
            "queryStringParameters": {
                "name": "test.csv"
            }
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], "https://test-url.com")
        mock_s3.generate_presigned_url.assert_called_once()

    def test_missing_name_parameter(self):
        event = {
            "queryStringParameters": {}
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Missing required query parameter", response['body'])

    def test_invalid_file_extension(self):
        event = {
            "queryStringParameters": {
                "name": "test.txt"
            }
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid file format", response['body'])

import unittest
from unittest.mock import patch, MagicMock
from src.functions.import_products_file import handler

class TestImportProductsFile(unittest.TestCase):
    @patch('src.functions.import_products_file.s3_client')
    def test_successful_url_generation(self, mock_s3):
        mock_s3.generate_presigned_url.return_value = "https://test-url.com"
        event = {
            "queryStringParameters": {
                "name": "test.csv"
            }
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], "https://test-url.com")
        mock_s3.generate_presigned_url.assert_called_once()

    def test_missing_name_parameter(self):
        event = {
            "queryStringParameters": {}
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Missing required query parameter", response['body'])

    def test_invalid_file_extension(self):
        event = {
            "queryStringParameters": {
                "name": "test.txt"
            }
        }

        response = handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid file format", response['body'])
