from flask import Flask, render_template, request, jsonify
import os
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        transcript = recognizer.recognize_sphinx(audio_data)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Error with recognition engine: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    audio_file = request.files["audio"]
    audio_path = "temp_audio.wav"

    sound = AudioSegment.from_file(audio_file, format="webm")
    sound = sound.set_frame_rate(16000).set_channels(1)
    sound.export(audio_path, format="wav")

    transcript = transcribe_audio(audio_path)
    os.remove(audio_path)

    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
