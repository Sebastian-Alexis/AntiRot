from flask import Flask, render_template, request, jsonify
import json
import re
from togetherai import smooth_translation
from wiki_indexer import scrape_wikipedia_glossary, save_to_json
import os
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import speech_recognition as sr
import subprocess

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

try:
    print("Updating definitions.json from Wikipedia...")
    glossary = scrape_wikipedia_glossary("https://en.wikipedia.org/wiki/Glossary_of_Generation_Z_slang")
    save_to_json(glossary, "definitions.json")
    print(f"Successfully updated definitions.json with {len(glossary)} terms.")
except Exception as e:
    print(f"Error updating definitions.json: {e}")

with open("definitions.json", "r", encoding="utf-8") as file:
    DEFINITIONS = json.load(file)

def translate_text(input_text):
    output_text = input_text
    for term, definition in sorted(DEFINITIONS.items(), key=lambda x: -len(x[0])):  
       
        pattern = r"\b" + re.escape(term) + r"\b"
        output_text = re.sub(pattern, f"[{definition}]", output_text, flags=re.IGNORECASE)
    return output_text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    input_text = data.get("text", "")
    rough_translation = translate_text(input_text)
    refined_translation, explanation = smooth_translation(rough_translation)
    return jsonify({"output": refined_translation, "explanation": explanation})

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    filename = secure_filename(audio_file.filename)
    webm_filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    wav_filepath = os.path.splitext(webm_filepath)[0] + ".wav"
    audio_file.save(webm_filepath)

    if os.path.getsize(webm_filepath) == 0:
        print("Uploaded file is empty.")
        return jsonify({"error": "Uploaded file is empty"}), 400

    try:
        result = subprocess.run(
            ["ffmpeg", "-f", "webm", "-i", webm_filepath, wav_filepath],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("FFmpeg output:", result.stderr.decode())

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_filepath) as source:
            audio_data = recognizer.record(source)
            transcribed_text = recognizer.recognize_google(audio_data)
        return jsonify({"transcription": transcribed_text})
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        return jsonify({"error": "Audio conversion failed"}), 500
    except sr.UnknownValueError:
        return jsonify({"error": "Audio was not clear enough to transcribe"}), 500
    except sr.RequestError as e:
        return jsonify({"error": f"Google API error: {e}"}), 500
    except Exception as e:
        print(f"Unexpected error during transcription: {e}")
        return jsonify({"error": "Unexpected server error"}), 500
    finally:
        if os.path.exists(webm_filepath):
            os.remove(webm_filepath)
        if os.path.exists(wav_filepath):
            os.remove(wav_filepath)

@app.route("/refresh_glossaries", methods=["POST"])
def refresh_glossaries():
    data = request.json
    links = data.get("links", "").split(",")
    updated_glossary = {}

    # Load existing definitions
    try:
        with open("definitions.json", "r", encoding="utf-8") as file:
            existing_glossary = json.load(file)
    except FileNotFoundError:
        existing_glossary = {}  # Start with an empty dictionary if the file doesn't exist
        print("definitions.json not found. Starting fresh.")

    # Scrape glossaries and merge them
    for link in links:
        try:
            print(f"Scraping glossary from {link.strip()}...")
            glossary = scrape_wikipedia_glossary(link.strip())
            updated_glossary.update(glossary)  # Add new terms
        except Exception as e:
            print(f"Error scraping {link.strip()}: {e}")

    # Debug: Check the size of the new terms
    print(f"New terms scraped: {len(updated_glossary)}")

    # Merge new terms with the existing glossary
    combined_glossary = {**existing_glossary, **updated_glossary}  # Ensure terms are merged without duplication

    # Debug: Check the total size after merging
    print(f"Total terms after merging: {len(combined_glossary)}")

    # Save updated definitions back to file
    try:
        with open("definitions.json", "w", encoding="utf-8") as file:
            json.dump(combined_glossary, file, ensure_ascii=False, indent=4)
        return jsonify({"message": f"Updated definitions.json with {len(combined_glossary)} total terms."})
    except Exception as e:
        print(f"Error saving definitions.json: {e}")
        return jsonify({"error": f"Failed to save glossary: {e}"}), 500




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
