from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
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

        # create Lambda functions
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

        # grant Lambda read access to the products table
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

        # create API Gateway
        api = apigateway.RestApi(
            self, 'ProductsApi',
            rest_api_name='Products Service',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        # create products resource and methods
        products = api.root.add_resource('products')
        products.add_method(
            'GET',
            apigateway.LambdaIntegration(get_products_list)
        )

        # add product/{productId} resource and GET method
        product_by_id = products.add_resource('{productId}')
        product_by_id.add_method(
            'GET',
            apigateway.LambdaIntegration(get_product_by_id)
        )

        # create Lambda function for creating products
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

        # grant Lambda write access to the Products and Stocks tables
        products_table.grant_write_data(create_product)
        stocks_table.grant_write_data(create_product)

        # add POST method to API Gateway
        products.add_method(
            'POST',
            apigateway.LambdaIntegration(create_product)
        )

        # output the API URL
        CfnOutput(
            self, 'ApiUrl',
            value=api.url,
            description='API Gateway URL'
        )

        # creating SQS queue
        catalog_items_queue = sqs.Queue(
            self, "CatalogItemsQueue",
            queue_name="catalogItemsQueue",
            visibility_timeout=Duration.seconds(30)
        )

        # creating SNS topic
        create_product_topic = sns.Topic(
            self, "CreateProductTopic",
            topic_name="createProductTopic"
        )

    

        # additional subscription for low-stock items
        # with different email using filters
        create_product_topic.add_subscription(
            sns_subs.EmailSubscription(
                "birli_pl@mail.ru",
                filter_policy={
                    "count": sns.SubscriptionFilter.numeric_filter({
                        "lessThan": 1
                    })
                }
            )
        )

        # adding email subscription
        create_product_topic.add_subscription(
            sns_subs.EmailSubscription("pavlova.jane@gmail.com")
        )

        catalog_batch_process = _lambda.Function(
            self, "CatalogBatchProcess",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="catalog_batch_process.handler",
            code=_lambda.Code.from_asset("src/functions"),  
            environment={
                "PRODUCTS_TABLE_NAME": products_table.table_name,
                "STOCKS_TABLE_NAME": stocks_table.table_name,
                "SNS_TOPIC_ARN": create_product_topic.topic_arn,             
            }
        )

        catalog_batch_process.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'sqs:receiveMessage',
                    'sqs:deleteMessage',
                ],
                resources=[
                    catalog_items_queue.queue_arn,
                ]
            )
        )

        # granting permissions
        products_table.grant_write_data(catalog_batch_process)
        stocks_table.grant_write_data(catalog_batch_process)
        create_product_topic.grant_publish(catalog_batch_process)

        # adding SQS trigger to Lambda
        catalog_batch_process.add_event_source(
            lambda_events.SqsEventSource(
                catalog_items_queue,
                batch_size=5
            )
        )

