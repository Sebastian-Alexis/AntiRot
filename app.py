from flask import Flask, render_template, request, jsonify
import json
import re
from togetherai import smooth_translation

app = Flask(__name__)

#load json - might need to fix when running on mac/lunx? not entirely sure - will update when loading onto raspberry pi
with open("definitions.json", "r", encoding="utf-8") as file:
    DEFINITIONS = json.load(file)

def translate_text(input_text):
    #replace
    output_text = input_text
    for term, definition in sorted(DEFINITIONS.items(), key=lambda x: -len(x[0])):  # Sort by term length (desc)
        #matching terms, case insensitive
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

if __name__ == "__main__":
    app.run(debug=True)
