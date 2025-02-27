import boto3
import uuid
from decimal import Decimal

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

products_table = dynamodb.Table('products')
stocks_table = dynamodb.Table('stocks')

products = [
    {"title": "Cashew Donut", "description": "Mmm with Nuts Tasty", "price": Decimal("7.05"), "count": 15},
    {"title": "Strawberry Donut", "description": "Super Tasty Strawberry", "price": Decimal("5.05"), "count": 20},
    {"title": "Chocolate Donut", "description": "Super Tasty Chocolate", "price": Decimal("5.00"), "count": 100},
]

def populate_tables():
    for product in products:
        product_id = str(uuid.uuid4())

        # Insert into products table
        products_table.put_item(Item={
            "id": product_id,
            "title": product["title"],
            "description": product["description"],
            "price": product["price"]
        })

        # Insert into stocks table
        stocks_table.put_item(Item={
            "product_id": product_id,
            "count": product["count"]
        })

        print(f"Added: {product['title']} (ID: {product_id}) with stock: {product['count']}")

if __name__ == "__main__":
    populate_tables()
