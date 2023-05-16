import os
import time
import boto3
import openai
import whisper
import aiofiles
from fastapi import FastAPI, UploadFile

app = FastAPI()
start = time.time()
model = whisper.load_model("base")
end = time.time()
print("Whisper Model load time: ", end - start)

session = boto3.session.Session()
client = session.client(service_name='secretsmanager', region_name='us-east-1')

openai.api_key = client.get_secret_value(
    SecretId='OPENAI_API_KEY')['SecretString']


@app.get("/")
async def root():
    return {"message": "Alive and well !!"}


@app.get("/heartbeat")
async def root():
    return {"message": "Beating fine !!"}


@app.post("/uploadaudio")
async def create_upload_file(in_file: UploadFile):
    # File chaina vaney error message handle garrney ...
    print("Filename : ", in_file.filename)
    async with aiofiles.open('audio.mp3', 'wb') as out_file:
        content = await in_file.read()
        await out_file.write(content)

        start = time.time()
        result = model.transcribe("audio.mp3")
        end = time.time()
        print('Time taken to transcribe: ', end - start)

        text_from_audio = result["text"]
        prompt = f'''
        Please generate a summary for this text below and make it such that it is not more than couple of sentences but not less than a sentence.: \n
        {text_from_audio}               
        '''
        print('Prompt: ', prompt)
        start = time.time()
        response = openai.Completion.create(model="text-davinci-003",
                                            prompt=prompt,
                                            temperature=0.6)
        end = time.time()
        print('Time taken to generate summary: ', end - start)
        print('Response: ', response)
    os.remove("audio.mp3")
    return response
