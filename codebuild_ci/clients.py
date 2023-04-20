import boto3


codebuild_client = boto3.client('codebuild')
logs_client = boto3.client('logs')
