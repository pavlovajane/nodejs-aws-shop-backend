from decimal import Decimal
import json
import os
from typing import Dict, Any
from mocks.products import products
import boto3
from botocore.exceptions import ClientError


def get_products_list(products_table):
    products_response = products_table.scan()
    products_list = products_response.get('Items', [])    
    return products_list

def get_stocks_dict(stocks_table):
    stocks_response = stocks_table.scan()
    stocks = {stock['product_id']: stock['count'] for stock in stocks_response.get('Items', [])}
    return stocks

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
    
def handler(event: Dict[str, Any], context: Any, dynamodb = None) -> Dict[str, Any]:
    try:
        dynamodb = boto3.resource('dynamodb') if not dynamodb else dynamodb
        products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE_NAME'])
        stocks_table = dynamodb.Table(os.environ['STOCKS_TABLE_NAME'])

        products = get_products_list(products_table)
        print(f"Fetched products: {products}")
    
        stocks = get_stocks_dict(stocks_table)
        print(f"Fetched stocks: {stocks}")

        for product in products:
            product_id = product['id']
            product['count'] = stocks.get(product_id, 0)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Enable CORS for frontend integration
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps(products, cls=DecimalEncoder)
        }
    except Exception as error:

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "body": json.dumps({"message": "Internal server error"})
        }
