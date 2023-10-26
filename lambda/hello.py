import json
from datetime import datetime,timezone,timedelta

def handler(event, context):
    return {
        'statusCode': 200,
        'body': f'Hello, AWS CDK! {datetime.now(timezone(timedelta(hours=9)))}'
    }
