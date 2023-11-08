import os
from aws_cdk import core, aws_lambda as _lambda, aws_apigateway as apigateway, aws_iam as iam

# API_KEY_ID = os.environ.get("API_KEY_ID")
# USAGE_PLAN_ID = os.environ.get("USAGE_PLAN_ID")


class ApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, env=core.Environment(region="ap-northeast-1"), **kwargs)
        
        # APIGatewayで呼ばれるlambda
        hello_lambda = _lambda.Function(
            self, 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='kokusenya_test',
            code=_lambda.Code.from_asset('../lambda'),
            handler='hello.handler',
        )
        
        goodmorning_lambda = _lambda.Function(
            self, 'GoodMorningHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='kokusenya_test2',
            code=_lambda.Code.from_asset('../lambda'),
            handler='goodmorning.handler',  # goodmorning.pyのhandler関数を指定
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
        deploy_options=apigateway.StageOptions(stage_name="dev"),policy=policy)

        # 既存のAPIキーを参照
        # existing_api_key = apigateway.ApiKey.from_api_key_id(self, "ExistingApiKey", api_key_id=API_KEY_ID)

        # リソースパスの作成
        api_v1 = api.root.add_resource("api").add_resource("v1")
        hello_resource = api_v1.add_resource("hello")
        good_morning_resource = api_v1.add_resource("goodmorning")
        
        
        # API Gatewayのモデルを定義（リクエストボディの検証）
        request_body_model = api.add_model(
            "RequestBodyModel",
            content_type="application/json",
            model_name="RequestBodyModel",
            schema=apigateway.JsonSchema(
                schema=apigateway.JsonSchemaVersion.DRAFT4,
                title="requestBody",
                type=apigateway.JsonSchemaType.OBJECT,
                properties={
                    "list_ids": apigateway.JsonSchema(
                        type=apigateway.JsonSchemaType.ARRAY,
                        items=apigateway.JsonSchema(type=apigateway.JsonSchemaType.STRING)
                    ),
                    "id1": apigateway.JsonSchema(
                        type=apigateway.JsonSchemaType.STRING
                    ),
                    "options": apigateway.JsonSchema(
                        type=apigateway.JsonSchemaType.OBJECT,
                        properties={
                            "optionKey": apigateway.JsonSchema(
                                type=apigateway.JsonSchemaType.STRING
                            )
                            # 他のキーもここに追加できます。
                        }
                    )
                },
                required=["list_ids", "id1"]  # 必須のフィールド
            )
        )


        # リソースにLambda関数を結びつける
        hello_resource.add_method("POST", apigateway.LambdaIntegration(hello_lambda),
            api_key_required=True,  # APIキーが必要とする設定
            request_models={"application/json": request_body_model}
        )
        good_morning_resource.add_method("POST", apigateway.LambdaIntegration(goodmorning_lambda),
            api_key_required=True,  # APIキーが必要とする設定
            request_models={"application/json": request_body_model}
        )

        # # APIキーをAPIステージに関連付ける
        # usage_plan = api.add_usage_plan("UsagePlan", api_key=existing_api_key)
        # usage_plan.add_api_stage(stage=api.deployment_stage)