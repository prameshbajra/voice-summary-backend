import os
import json
import boto3

PRESIGNED_URL_EXPIRATION_DURATION_SECONDS = int(os.environ.get(
    'PRESIGNED_URL_EXPIRATION_DURATION_SECONDS', '3600')) 
S3_BUCKET = os.environ.get('S3_BUCKET')


def handler(event, context):
    s3_client = boto3.client('s3')
    try:
        object_key = event['queryStringParameters']['key']
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': object_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION_DURATION_SECONDS)
    except TypeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Query parameter not available.')
        }

    return {'statusCode': 200, 'body': json.dumps(response)}
