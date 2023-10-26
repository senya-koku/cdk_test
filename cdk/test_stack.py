import os
from aws_cdk import core, aws_lambda as _lambda, aws_apigateway as apigateway, aws_iam as iam
from aws_cdk.aws_apigateway import CfnUsagePlan, CfnUsagePlanKey


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
            deploy_options=apigateway.StageOptions(stage_name="dev")
        )

        # リソースパスの作成
        api_root = api.root.add_resource("api").add_resource("v1").add_resource("hello")

        # 既存のAPIキーを取得
        existing_api_key = apigateway.ApiKey.from_api_key_id(self, "ExistingApiKey", api_key_id=API_KEY_ID)

        # # 既存の使用量プランを取得
        # existing_usage_plan = apigateway.UsagePlan.from_usage_plan_id(self, "ExistingUsagePlan", USAGE_PLAN_ID)

        # # 使用量プランにAPIキーを関連付ける
        # existing_usage_plan.add_api_key(existing_api_key)

        # # 使用量プランにAPIステージを関連付ける
        # existing_usage_plan.add_stage(api=api, stage=api.deployment_stage)

        # 既存の使用量プランを取得
        #existing_usage_plan = CfnUsagePlan.from_usage_plan_attributes(self, "ExistingUsagePlan", usage_plan_id=USAGE_PLAN_ID)

        # 使用量プランにAPIステージを関連付ける
        api_stage = CfnUsagePlanKey(
            self, "ApiStageKey",
            key_id=existing_api_key.key_id,
            key_type="API_KEY",
            usage_plan_id=USAGE_PLAN_ID,
            value=api.deployment_stage.stage_name
        )

        # # リソースにLambda関数を結びつける
        # api_root.add_method("POST", apigateway.LambdaIntegration(lambda_function), 
        #     request_parameters={
        #         "method.request.querystring.user_id": True
        #     }
        # )


