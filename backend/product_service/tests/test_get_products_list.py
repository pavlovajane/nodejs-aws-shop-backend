# tests/test_get_products_list.py
import os
import json
import boto3
import pytest

def test_get_products_list_success(api_gateway_event, lambda_context, mock_products, dynamodb_mock):
    """Test successful retrieval of products list"""

    from src.functions.get_products_list import handler

    # Execute
    response = handler(api_gateway_event(), lambda_context, dynamodb_mock)
    
    # Assert
    assert response['statusCode'] == 200
    assert 'body' in response
    
    body = json.loads(response['body'])
    assert isinstance(body, list)
    assert len(body) == len(mock_products)
    
    # Verify CORS headers
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert response['headers']['Access-Control-Allow-Credentials'] is True

def test_get_products_list_structure(api_gateway_event, lambda_context, dynamodb_mock):
    """Test the structure of returned products"""
    # Execute
    from src.functions.get_products_list import handler
    response = handler(api_gateway_event(), lambda_context, dynamodb_mock)
    body = json.loads(response['body'])
    
    # Assert structure of first product
    product = body[0]
    assert all(key in product for key in ['id', 'title', 'description', 'price'])
    assert isinstance(product['id'], str)
    assert isinstance(product['price'], (int, float, str))

def test_get_products_list_error_handling(api_gateway_event, lambda_context, mocker):
    """Test error handling when something goes wrong"""
    # Mock an error
    mocker.patch('src.functions.get_products_list.products', side_effect=Exception("Test error"))
    
    # Execute
    from src.functions.get_products_list import handler
    response = handler(api_gateway_event(), lambda_context)
    
    # Assert
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['message'] == 'Internal server error'
