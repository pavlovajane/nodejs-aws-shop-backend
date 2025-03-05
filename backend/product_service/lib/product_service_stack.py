from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    CfnOutput
)
from constructs import Construct
import os

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        products_table = dynamodb.Table.from_table_name(
            self, "ProductsTable", "products"
        )

        stocks_table = dynamodb.Table.from_table_name(
            self, "StocksTable", "stocks"
        )

        # Create Lambda functions
        get_products_list = _lambda.Function(
            self, 'GetProductsListFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='get_products_list.handler',
            code=_lambda.Code.from_asset('src/functions'),
            environment={
                "PRODUCTS_TABLE_NAME": products_table.table_name,
                "PRODUCTS_TABLE_ARN": products_table.table_arn,
                "STOCKS_TABLE_NAME": stocks_table.table_name,
                "STOCKS_TABLE_ARN": stocks_table.table_arn,
            }
        )

        # Grant Lambda read access to the products table
        products_table.grant_read_data(get_products_list)
        stocks_table.grant_read_data(get_products_list)

        get_product_by_id = _lambda.Function(
            self, 'GetProductByIdFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='get_product_by_id.handler',
            code=_lambda.Code.from_asset('src/functions'),
            environment={
                "PRODUCTS_TABLE_NAME": products_table.table_name,
                "PRODUCTS_TABLE_ARN": products_table.table_arn,
                "STOCKS_TABLE_NAME": stocks_table.table_name,
                "STOCKS_TABLE_ARN": stocks_table.table_arn,
            }
        )

        products_table.grant_read_data(get_product_by_id)
        stocks_table.grant_read_data(get_product_by_id)

        # Create API Gateway
        api = apigateway.RestApi(
            self, 'ProductsApi',
            rest_api_name='Products Service',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        # Create products resource and methods
        products = api.root.add_resource('products')
        products.add_method(
            'GET',
            apigateway.LambdaIntegration(get_products_list)
        )

        # Add product/{productId} resource and GET method
        product_by_id = products.add_resource('{productId}')
        product_by_id.add_method(
            'GET',
            apigateway.LambdaIntegration(get_product_by_id)
        )

        # Create Lambda function for creating products
        create_product = _lambda.Function(
            self, 'CreateProductFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='create_product.handler',
            code=_lambda.Code.from_asset('src/functions'),
            environment={
                "PRODUCTS_TABLE_NAME": products_table.table_name,
                "STOCKS_TABLE_NAME": stocks_table.table_name,
            }
        )

        # Grant Lambda write access to the Products and Stocks tables
        products_table.grant_write_data(create_product)
        stocks_table.grant_write_data(create_product)

        # Add POST method to API Gateway
        products.add_method(
            'POST',
            apigateway.LambdaIntegration(create_product)
        )

        # Output the API URL
        CfnOutput(
            self, 'ApiUrl',
            value=api.url,
            description='API Gateway URL'
        )
