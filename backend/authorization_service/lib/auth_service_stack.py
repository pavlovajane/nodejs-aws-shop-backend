from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Fn as cdkFn,
    CfnOutput
)
from constructs import Construct
import os
from dotenv import load_dotenv
    
load_dotenv()

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

        # Grant API Gateway permission to invoke the Lambda function
        auth_request_lambda.add_permission(
            "ApiGatewayInvoke",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction"
        )
        
        CfnOutput(
            self, "AuthorizerLambdaArn",
            value=auth_request_lambda.function_arn,
            export_name="AuthorizerLambdaArn"
        )
