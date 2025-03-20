from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct


class ImportServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        products_table = dynamodb.Table.from_table_name(
            self, "ProductsTable", "products"
        )

        stocks_table = dynamodb.Table.from_table_name(
            self, "StocksTable", "stocks"
        )

        import_bucket = s3.Bucket.from_bucket_name(
            self, 
            'ImportBucket', 
            'bucket-for-files-import'
        )

        import_products_file = lambda_.Function(
            self, 
            'ImportProductsFile',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='import_products_file.handler',
            code=lambda_.Code.from_asset('src/functions'),
            environment={
                "BUCKET_NAME": "bucket-for-files-import",        
            }
        )

        import_file_parser = lambda_.Function(
            self, 
            'ImportFileParser',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='import_file_parser.handler',
            code=lambda_.Code.from_asset('src/functions'),
            timeout=Duration.seconds(30),  # Increase timeout for file processing
            environment={
                "BUCKET_NAME": "bucket-for-files-import",
                "PRODUCTS_TABLE_NAME": "products",
                "STOCKS_TABLE_NAME": "stocks",
                "SQS_QUEUE_URL": "https://sqs.us-east-2.amazonaws.com/904233116615/catalogItemsQueue"
            }
        )

        import_products_file.add_to_role_policy(
            iam.PolicyStatement(
                actions=['s3:PutObject'],
                resources=[
                    f"{import_bucket.bucket_arn}/uploaded/*",
                ]
            )
        )

        import_file_parser.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    's3:GetObject',
                    's3:CopyObject',
                    's3:DeleteObject',
                    's3:PutObject',
                ],
                resources=[
                    f"{import_bucket.bucket_arn}/uploaded/*",
                    f"{import_bucket.bucket_arn}/parsed/*"
                ]
            )
        )

        import_file_parser.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    'sqs:sendmessage',
                ],
                resources=[
                    "arn:aws:sqs:us-east-2:904233116615:catalogItemsQueue",
                ]
            )
        )

        products_table.grant_write_data(import_file_parser)
        stocks_table.grant_write_data(import_file_parser)

        import_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(import_file_parser),
            s3.NotificationKeyFilter(prefix="uploaded/")
        )

        api = apigateway.RestApi(
            self, 
            'ImportApi',
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS
            )
        )

        import_integration = apigateway.LambdaIntegration(import_products_file)
    
        import_resource = api.root.add_resource('import')

        method_options = apigateway.MethodOptions(
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer="ApiAuthorizer"
        )
    
        import_resource.add_method(
            'GET',
            import_integration,
            method_options=method_options,
            request_parameters={
                'method.request.querystring.name': True
            }
        )

        CfnOutput(
            self, 
            'ApiUrl',
            value=api.url,
            description='API Gateway endpoint URL'
        )
