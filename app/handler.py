import time
import boto3
import openai
import whisper

start = time.time()
model = whisper.load_model("base")
end = time.time()
print("Whisper Model load time: ", end - start)

session = boto3.session.Session()
client = session.client(service_name='secretsmanager', region_name='us-east-1')

openai.api_key = client.get_secret_value(
    SecretId='OPENAI_API_KEY')['SecretString']


def handler(event, context):
    return {
        "statusCode": 200,
        "event": event,
    }
