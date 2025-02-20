# tests/test_get_products_list.py
import json
import pytest
from src.functions.get_products_list import handler

def test_get_products_list_success(api_gateway_event, lambda_context, mock_products):
    """Test successful retrieval of products list"""
    # Execute
    response = handler(api_gateway_event(), lambda_context)
    
    # Assert
    assert response['statusCode'] == 200
    assert 'body' in response
    
    body = json.loads(response['body'])
    assert isinstance(body, list)
    assert len(body) == len(mock_products)
    
    # Verify CORS headers
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert response['headers']['Access-Control-Allow-Credentials'] is True

def test_get_products_list_structure(api_gateway_event, lambda_context):
    """Test the structure of returned products"""
    # Execute
    response = handler(api_gateway_event(), lambda_context)
    body = json.loads(response['body'])
    
    # Assert structure of first product
    product = body[0]
    assert all(key in product for key in ['id', 'title', 'description', 'price', 'count'])
    assert isinstance(product['id'], str)
    assert isinstance(product['price'], (int, float))
    assert isinstance(product['count'], int)

def test_get_products_list_error_handling(api_gateway_event, lambda_context, mocker):
    """Test error handling when something goes wrong"""
    # Mock an error
    mocker.patch('src.functions.get_products_list.products', side_effect=Exception("Test error"))
    
    # Execute
    response = handler(api_gateway_event(), lambda_context)
    
    # Assert
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['message'] == 'Internal server error'
