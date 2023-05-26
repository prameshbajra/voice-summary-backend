import os
import time
import boto3
from whisperx import load_model, load_audio

start = time.time()
model = load_model("base",
                   device="cpu",
                   compute_type="int8",
                   language="en",
                   download_root='/tmp/')
end = time.time()
print("Whisper Model load time: ", end - start)

session = boto3.session.Session()
s3_client = boto3.client('s3')
batch_size = 4


def handler(event, context):
    # Get the bucket name and the key for the uploaded S3 object
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    print("Downloading: ", bucket, key)
    # Define the path to save the file in the /tmp directory
    download_path = os.path.join('/tmp', os.path.basename(key))
    # Download the file from S3 to the /tmp directory
    s3_client.download_file(bucket, key, download_path)
    print("Done downloading. :D")
    start = time.time()

    audio = load_audio(download_path)
    print(f"Audio Loaded: {time.time() - start}")
    result = model.transcribe(audio, batch_size=batch_size)
    print(f"Transcribed: {time.time() - start}")

    print("Result: ", result)
    return {
        "statusCode": 200,
        "result": result,
    }
