import os
import time
import whisper
import aiofiles
from fastapi import FastAPI, UploadFile

app = FastAPI()
start = time.time()
model = whisper.load_model("base")
end = time.time()
print("Whisper Model load time: ", end - start)

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
    print("List: ", os.listdir())
    os.remove("audio.mp3")
    return {"hey": "hmmmm"}