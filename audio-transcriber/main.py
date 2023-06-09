import os
import time
import firebase_admin
from firebase_admin import firestore
from firebase_admin import storage
from flask import Flask, request
from whisperx import load_model, load_audio

bucket_name = 'voice-summary-app-eba91.appspot.com'

app = Flask(__name__)

default_app = firebase_admin.initialize_app()
db = firestore.client()
bucket = storage.bucket(bucket_name)

start = time.time()
model = load_model("base",
                   device="cpu",
                   compute_type="int8",
                   language="en",
                   download_root='/tmp/')
end = time.time()
print("Whisper Model load time: ", end - start)
batch_size = 16

@app.route("/", methods=['GET'])
def transcribe_audio():
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

        memo_ref.update({
            u'transcript': result
        })

        print("Result: ", result)

    except:
        print(u'No such document!')

    return f"Hello {name}!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))