from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import uuid
from threading import Thread
from Photomeme import generate_photo_memes

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
PHOTO_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "photo_memes")
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PHOTO_OUTPUT_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Store task states
tasks = {}  # { task_id: None | [urls] | {"error": "..."} }

def process_input(task_id, input_path, input_type="video"):
    """
    Background processing for youtube/video/photo
    """
    try:
        meme_files = []

        if input_type in ["youtube", "video"]:
            # Run video pipeline
            command = f'python allfour.py --input "{input_path}"'
            subprocess.run(command, shell=True, check=True)

            # Collect latest meme outputs
            files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
            meme_files = [f"http://127.0.0.1:5000/outputs/{f}" for f in files[:6]]

        elif input_type == "photo":
            output_files = generate_photo_memes(input_path)
            meme_files = [f"http://127.0.0.1:5000/outputs/photo_memes/{f}" for f in output_files]

        tasks[task_id] = meme_files

    except Exception as e:
        tasks[task_id] = {"error": str(e)}


@app.route('/upload', methods=['POST'])
def upload():
    try:
        input_path = None
        input_type = None

        # Handle YouTube JSON input
        if request.is_json:
            data = request.get_json()
            youtube_link = data.get('youtubeLink')
            if not youtube_link:
                return jsonify({"success": False, "error": "No YouTube link provided."})
            input_path = youtube_link
            input_type = "youtube"

        # Handle file uploads
        else:
            video_file = request.files.get('videoFile')
            photo_file = request.files.get('photoFile')

            if video_file:
                input_path = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}_{video_file.filename}")
                video_file.save(input_path)
                input_type = "video"

            elif photo_file:
                input_path = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}_{photo_file.filename}")
                photo_file.save(input_path)
                input_type = "photo"

            else:
                return jsonify({"success": False, "error": "No input provided."})

        # Create task ID
        task_id = str(uuid.uuid4())
        tasks[task_id] = None  # mark pending

        # Process in background
        thread = Thread(target=process_input, args=(task_id, input_path, input_type))
        thread.start()

        return jsonify({"success": True, "task_id": task_id})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/status/<task_id>')
def status(task_id):
    if task_id not in tasks:
        return jsonify({"success": False, "error": "Invalid task ID"})

    result = tasks[task_id]

    if result is None:
        return jsonify({"ready": False})
    elif isinstance(result, dict) and "error" in result:
        return jsonify({"ready": True, "success": False, "error": result["error"]})
    else:
        return jsonify({"ready": True, "success": True, "memes": result})


@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


@app.route('/get_memes')
def get_memes():
    meme_files = sorted(os.listdir(OUTPUT_DIR))[:6]
    meme_urls = [f'/outputs/{fname}' for fname in meme_files]
    return jsonify({'memes': meme_urls})


@app.route('/custom_caption', methods=['POST'])
def custom_caption():
    data = request.json
    meme_file = data.get('meme_file')
    caption = data.get('caption')
    custom = data.get('custom')  # 'y' or 'n'
    # Process the custom caption as needed
    # ...
    return jsonify({'success': True})


if __name__ == "__main__":
    app.run(debug=True)
