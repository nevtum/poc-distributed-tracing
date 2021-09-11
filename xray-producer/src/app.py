import json
import boto3
from aws_xray_sdk.core import patch_all
from uuid import uuid4
from os import environ

queue = boto3.resource("sqs").Queue(url=environ["QUEUE_URL"])

patch_all()

def lambda_handler(event, context):
    payload = {
        "id": str(uuid4()),
        "message": "Hello, World!"
    }
    queue.send_message(MessageBody=json.dumps(payload))