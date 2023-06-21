import os
import time
import datetime
from functools import reduce
import firebase_admin
from firebase_admin import firestore
from firebase_admin import storage
from flask import Flask, request
from whisperx import load_model, load_audio
import threading
import psutil

bucket_name = 'voice-summary-app-eba91.appspot.com'

app = Flask(__name__)

default_app = firebase_admin.initialize_app()
db = firestore.client()
bucket = storage.bucket(bucket_name)

start = time.time()
model = load_model("base",
                   device="cpu",
                   compute_type="int8",
                   language="en")
end = time.time()
print("Whisper Model load time: ", end - start)
batch_size = 16

# Global variables to store the max CPU and memory usage
max_cpu = 0
max_mem = 0

def profile():
    global max_cpu
    global max_mem
    while True:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        max_cpu = max(max_cpu, cpu)
        max_mem = max(max_mem, mem)
        time.sleep(0.1)

@app.route("/", methods=['GET'])
def transcribe_audio():
    global max_cpu
    global max_mem
    max_cpu = 0
    max_mem = 0

    profiling_thread = threading.Thread(target=profile)
    profiling_thread.start()

    memo_id = request.args.get('memoId')

    if not memo_id:
        return "No memoId provided", 400
    
    memo_ref = db.collection(u'memos').document(memo_id)

    try:
        doc = memo_ref.get()
        print(u'Document data: {}'.format(doc.to_dict()))
        audio_src = doc.to_dict()['audioSrc']

        download_path = os.path.join('/tmp', os.path.basename(audio_src))
        blob = bucket.blob(audio_src)
        blob.download_to_filename(download_path)

        start = time.time()

        audio = load_audio(download_path)
        print(f"Audio Loaded: {time.time() - start}")
        result = model.transcribe(audio, batch_size=batch_size)
        print(f"Transcribed: {time.time() - start}")

        transcription_reducer = lambda transcript: reduce(lambda acc, segment: acc + segment['text'] + " ", [segment for segment in transcript['segments']], "")
        transcript_text = transcription_reducer(result)
        print("Result: ", result)
        print("Reduced Result: ", transcript_text)

        updated_time = int(datetime.datetime.now().timestamp() * 1000)

        memo_ref.update({
            u'transcript': transcript_text,
            u'updatedDate': updated_time
        })


    except Exception as e:
        print(u'No such document!')
        print(f'Error with document {memo_id}: {str(e)}')

    profiling_thread.do_run = False
    profiling_thread.join()

    print(f"Max CPU usage: {max_cpu}%")
    print(f"Max memory usage: {max_mem}%")

    memo_ref.update({
        u'cpuUsage': max_cpu,
        u'memoryUsage': max_mem
    })

    return f"Success"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))