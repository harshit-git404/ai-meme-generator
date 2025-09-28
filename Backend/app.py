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
            output_path = generate_photo_memes(input_path)
            if output_path:
                filename = os.path.basename(output_path)
                meme_files = [f"http://127.0.0.1:5000/outputs/photo_memes/{filename}"]
            else:
                meme_files = []

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
        
@app.route('/results/<task_id>')
def get_results(task_id):
    """Get results for a specific task"""
    if task_id not in tasks:
        return jsonify({"success": False, "error": "Invalid task ID"})

    result = tasks[task_id]

    if result is None:
        return jsonify({"success": False, "ready": False})
    elif isinstance(result, dict) and "error" in result:
        return jsonify({"success": False, "ready": True, "error": result["error"]})
    else:
        return jsonify({"success": True, "ready": True, "memes": result})


@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)



@app.route('/get_memes')
def get_memes():
    # Reuse the get_all_memes logic for consistency
    return get_all_memes()


@app.route('/get_all_memes')
def get_all_memes():
    # Check both output directories for memes
    all_memes = []
    
    # Check main output directory
    if os.path.exists(OUTPUT_DIR):
        main_files = [f for f in os.listdir(OUTPUT_DIR) 
                     if os.path.isfile(os.path.join(OUTPUT_DIR, f)) 
                     and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm'))]
        main_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
        all_memes.extend([f"http://127.0.0.1:5000/outputs/{f}" for f in main_files])
    
    # Check photo memes directory
    if os.path.exists(PHOTO_OUTPUT_DIR):
        photo_files = [f for f in os.listdir(PHOTO_OUTPUT_DIR) 
                      if os.path.isfile(os.path.join(PHOTO_OUTPUT_DIR, f)) 
                      and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        photo_files.sort(key=lambda x: os.path.getmtime(os.path.join(PHOTO_OUTPUT_DIR, x)), reverse=True)
        all_memes.extend([f"http://127.0.0.1:5000/outputs/photo_memes/{f}" for f in photo_files])
    
    # Sort all memes by modification time (newest first)
    all_memes_with_time = []
    for url in all_memes:
        if '/outputs/photo_memes/' in url:
            file_path = os.path.join(PHOTO_OUTPUT_DIR, url.split('/')[-1])
        else:
            file_path = os.path.join(OUTPUT_DIR, url.split('/')[-1])
        
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            all_memes_with_time.append((url, mtime))
    
    # Sort by modification time (newest first) and take top 6
    all_memes_with_time.sort(key=lambda x: x[1], reverse=True)
    top_memes = [url for url, _ in all_memes_with_time[:6]]
    
    return jsonify({'memes': top_memes})


@app.route('/outputs/photo_memes/<path:filename>')
def serve_photo_output(filename):
    return send_from_directory(PHOTO_OUTPUT_DIR, filename)




## Custom caption functionality disabled intentionally.
## Endpoint removed to simplify backend while feature is paused.


# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory('../Frontend', 'index.html')

@app.route('/results.html')
def serve_results():
    return send_from_directory('../Frontend', 'results.html')

@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory('../Frontend', path)

if __name__ == "__main__":
    # Run without auto-reloader to avoid duplicate model loads
    app.run(debug=False)
