# tests/conftest.py
import pytest
from src.functions.mocks.products import products

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
