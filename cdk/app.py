from aws_cdk import core
from test_stack import ApiStack

class MyCdkApp(core.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # スタックのインスタンスを作成し、アプリケーションに関連付ける
        ApiStack(self, "MyApiStack")

# アプリケーションのインスタンスを作成
app = MyCdkApp()

# アプリケーションの実行
app.synth()
