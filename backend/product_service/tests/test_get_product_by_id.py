# tests/test_get_product_by_id.py
import json
import pytest
from src.functions.get_product_by_id import handler

def test_get_product_by_id_success(api_gateway_event, lambda_context, mock_products):
    """Test successful retrieval of a product by ID"""
    # Prepare
    product_id = mock_products[0]['id']
    event = api_gateway_event(path_parameters={"productId": product_id})
    
    # Execute
    response = handler(event, lambda_context)
    
    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['data']['id'] == product_id
    assert 'title' in body['data']
    assert 'price' in body['data']

def test_get_product_by_id_not_found(api_gateway_event, lambda_context):
    """Test response when product is not found"""
    # Prepare
    event = api_gateway_event(path_parameters={"productId": "nonexistent-id"})
    
    # Execute
    response = handler(event, lambda_context)
    
    # Assert
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['message'] == 'Product not found'
    assert body['error']['code'] == 'PRODUCT_NOT_FOUND'

def test_get_product_by_id_missing_parameter(api_gateway_event, lambda_context):
    """Test response when productId is missing"""
    # Execute
    response = handler(api_gateway_event(), lambda_context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['message'] == 'Bad Request: Missing productId parameter'

def test_get_product_by_id_empty_parameter(api_gateway_event, lambda_context):
    """Test response when productId is empty"""
    # Prepare
    event = api_gateway_event(path_parameters={"productId": ""})
    
    # Execute
    response = handler(event, lambda_context)
    
    # Assert
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['message'] == 'Bad Request: ProductId cannot be empty'


