import os
from aws_cdk import core, aws_lambda as _lambda, aws_apigateway as apigateway, aws_iam as iam

API_KEY_ID = os.environ.get("API_KEY_ID")
USAGE_PLAN_ID = os.environ.get("USAGE_PLAN_ID")


class ApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, env=core.Environment(region="ap-northeast-1"), **kwargs)
        
        # APIGatewayで呼ばれるlambda
        lambda_function = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='kokusenya_test',
            code=_lambda.Code.from_asset('../lambda'),
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
        api = apigateway.RestApi(self, 'kokusenya_test',
        deploy_options=apigateway.StageOptions(stage_name="dev"),
        policy=policy  # この行を追加
    )

        # 既存のAPIキーを参照
        existing_api_key = apigateway.ApiKey.from_api_key_id(self, "ExistingApiKey", api_key_id=API_KEY_ID)

        # リソースパスの作成
        api_root = api.root.add_resource("api").add_resource("v1").add_resource("hello")

        # リソースにLambda関数を結びつける
        api_method = api_root.add_method("POST", apigateway.LambdaIntegration(lambda_function), 
            api_key_required=True,  # APIキーが必要とする設定
            request_parameters={
                "method.request.querystring.id1": True
            }
        )

        # APIキーをAPIステージに関連付ける
        usage_plan = api.add_usage_plan("UsagePlan", api_key=existing_api_key)
        usage_plan.add_api_stage(stage=api.deployment_stage)