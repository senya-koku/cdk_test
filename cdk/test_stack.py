from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_iam as iam

class ApiStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # APIGatewayで呼ばれるlambda
        lambda_function = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='Hello',
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )

        # IP制限のポリシーを定義
        policy = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=["execute-api:Invoke"],
                    resources=["*"],
                    conditions={
                        "NotIpAddress": {
                            "aws:SourceIp": "113.43.247.220"
                        }
                    },
                    principals=[iam.ArnPrincipal('*')]
                )
            ]
        )

        # apiGatewayを用意する
        api = apigateway.LambdaRestApi(
            self, 'hello-api',
            handler=lambda_function,
            policy=policy
        )

