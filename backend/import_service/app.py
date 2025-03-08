#!/usr/bin/env python3
import aws_cdk as cdk
from lib.import_service_stack import ImportServiceStack

app = cdk.App()
ImportServiceStack(app, "ImportServiceStack")
app.synth()
