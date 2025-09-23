# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# import subprocess
# import os
# import uuid

# app = Flask(__name__)
# CORS(app)  # Allow requests from frontend

# OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# @app.route('/upload', methods=['POST'])
# def upload():
#     try:
#         youtube_link = None
#         video_file = None
#         photo_file = None

#         # Check if JSON (YouTube link)
#         if request.is_json:
#             data = request.get_json()
#             youtube_link = data.get('youtubeLink')

#         # Else, handle uploaded files
#         else:
#             video_file = request.files.get('videoFile')
#             photo_file = request.files.get('photoFile')

#             # Save uploaded files to downloads folder
#             if video_file:
#                 video_path = os.path.join("downloads", f"{uuid.uuid4()}_{video_file.filename}")
#                 video_file.save(video_path)
#                 youtube_link = video_path  # pass path instead of link
#             if photo_file:
#                 photo_path = os.path.join("downloads", f"{uuid.uuid4()}_{photo_file.filename}")
#                 photo_file.save(photo_path)
#                 youtube_link = photo_path  # pass path instead of link

#         # Call allfour.py with the input
#         command = f'python allfour.py --input "{youtube_link}"'
#         subprocess.run(command, shell=True, check=True)

#         # After allfour.py finishes, get top 6 meme outputs
#         meme_files = os.listdir(OUTPUT_DIR)
#         meme_files = [f for f in meme_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
#         meme_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)

#         memes = [f"http://127.0.0.1:5000/outputs/{f}" for f in meme_files[:6]]

#         return jsonify({"success": True, "memes": memes})

#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)})

# # Serve output files
# @app.route('/outputs/<filename>')
# def serve_output(filename):
#     return send_from_directory(OUTPUT_DIR, filename)

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import uuid
from threading import Thread

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Keep track of tasks
tasks = {}

def process_input(task_id, input_path, is_youtube=False):
    try:
        # Build command
        if is_youtube:
            command = f'python allfour.py --input "{input_path}"'
        else:
            command = f'python allfour.py --input "{input_path}"'

        # Run long process
        subprocess.run(command, shell=True, check=True)

        # Get top 6 meme files
        meme_files = os.listdir(OUTPUT_DIR)
        meme_files = [f for f in meme_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        meme_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)

        tasks[task_id] = [f"http://127.0.0.1:5000/outputs/{f}" for f in meme_files[:6]]

    except Exception as e:
        tasks[task_id] = {"error": str(e)}

@app.route('/upload', methods=['POST'])
def upload():
    try:
        input_path = None
        is_youtube = False

        if request.is_json:
            data = request.get_json()
            youtube_link = data.get('youtubeLink')
            if not youtube_link:
                return jsonify({"success": False, "error": "No YouTube link provided."})
            input_path = youtube_link
            is_youtube = True
        else:
            video_file = request.files.get('videoFile')
            photo_file = request.files.get('photoFile')

            if video_file:
                input_path = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}_{video_file.filename}")
                video_file.save(input_path)
            elif photo_file:
                input_path = os.path.join(DOWNLOADS_DIR, f"{uuid.uuid4()}_{photo_file.filename}")
                photo_file.save(input_path)
            else:
                return jsonify({"success": False, "error": "No input provided."})

        # Generate task ID
        task_id = str(uuid.uuid4())
        tasks[task_id] = None

        # Start background processing
        thread = Thread(target=process_input, args=(task_id, input_path, is_youtube))
        thread.start()

        # Return task ID immediately
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

@app.route('/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
