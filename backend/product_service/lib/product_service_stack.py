from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    CfnOutput
)
from constructs import Construct
import os

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        get_products_list = _lambda.Function(
            self, 'GetProductsListFunction',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='get_products_list.handler',
            code=_lambda.Code.from_asset('src/functions'),
            environment={
                # Add environment variables if needed
            }
        )

        # Create API Gateway
        api = apigateway.RestApi(
            self, 'ProductsApi',
            rest_api_name='Products Service',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        # Create products resource and GET method
        products = api.root.add_resource('products')
        products.add_method(
            'GET',
            apigateway.LambdaIntegration(get_products_list)
        )

        # Output the API URL
        CfnOutput(
            self, 'ApiUrl',
            value=api.url,
            description='API Gateway URL'
        )
