#!/usr/bin/env python3
import aws_cdk as cdk
from lib.product_service_stack import ProductServiceStack

app = cdk.App()
ProductServiceStack(app, "ProductServiceStack")
app.synth()
