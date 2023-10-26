from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
)
class ApiStack(Stack):
    def __init__(self, scope:Construct, id:str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # APIGatewayで呼ばれるlambda
        lambda_function = _lambda.Function(
            self, 'HelloHandler',
            runtime = _lambda.Runtime.PYTHON_3_8,
            function_name = 'Hello',
            code = _lambda.Code.from_asset('lambda'),
            handler = 'hello.handler',
        )

        # apiGatewayを用意する
        api = apigateway.LambdaRestApi(
            self, 'hello-api',
            handler = lambda_function
        )
