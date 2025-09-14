from flask import Flask, request, jsonify
import os
from visualProcess import process_visual
# If you have verbal modules, import them
# from verbalLocal import process_verbal_local
# from verbalLink import process_verbal_link

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Expects either:
      - file upload (video), OR
      - JSON body with {"url": "<youtube_url>"}
    """
    if "file" in request.files:  # local video upload
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Run local analysis
        # Replace with verbal processing if you have it
        # verbal = process_verbal_local(filepath)
        visual = process_visual(filepath)
        verbal = None  # Placeholder

    elif request.is_json and "url" in request.json:  # YouTube link
        url = request.json["url"]

        # Run link analysis
        # verbal = process_verbal_link(url)
        visual = process_visual(url)
        verbal = None  # Placeholder

    else:
        return jsonify({"error": "Please provide a video file or a YouTube URL"}), 400

    # Standardized JSON response
    result = {
        "verbal": verbal,
        "visual": visual
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
