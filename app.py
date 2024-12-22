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
        transcript = recognizer.recognize_google(audio_data)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Error with Google Speech Recognition: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    try:
        print("Request received")
        print("Files:", request.files)

        if "audio" not in request.files:
            print("No audio file in request")
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        print("Audio file received:", audio_file.filename)

        audio_path = "temp_audio.wav"

        try:
            sound = AudioSegment.from_file(audio_file, format="webm")
            sound = sound.set_frame_rate(16000).set_channels(1)
            sound.export(audio_path, format="wav")
        except Exception as conversion_error:
            print("Audio conversion error:", conversion_error)
            return jsonify({"error": f"Audio conversion error: {conversion_error}"}), 500

        try:
            transcript = transcribe_audio(audio_path)
            os.remove(audio_path)
        except Exception as transcription_error:
            print("Transcription error:", transcription_error)
            return jsonify({"error": f"Transcription error: {transcription_error}"}), 500

        print("Transcript:", transcript)
        return jsonify({"transcript": transcript})
    except Exception as e:
        print("Error processing audio:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
