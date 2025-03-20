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
import os

class AuthServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        auth_request_lambda = lambda_.Function(
            self,
            'AuthRequest',
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler='basic_authorizer.handler',
            code=lambda_.Code.from_asset('src/functions'),
            environment={
                "pavlovajane": os.environ['pavlovajane'],
            }
        )

        apigateway.RequestAuthorizer(
            self,
            'ApiAuthorizer',
            handler=auth_request_lambda,
            identity_sources=[apigateway.IdentitySource.header('Authorization')],
            results_cache_ttl=Duration.seconds(0)
        )
        
        CfnOutput(
            self, 
            'ApiUrl',
            value=api.url,
            description='API Gateway endpoint URL'
        )
