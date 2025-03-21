#!/usr/bin/env python3
import aws_cdk as cdk
from lib.auth_service_stack import AuthServiceStack

app = cdk.App()
AuthServiceStack(app, "AuthServiceStack")
app.synth()
