from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import sys
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
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory containing app.py
            allfour_path = os.path.join(script_dir, "allfour.py")
            try:
                subprocess.run([sys.executable, allfour_path, "--input", input_path], 
                            check=True,
                            cwd=script_dir)  # Set working directory to Backend folder
            except subprocess.CalledProcessError as e:
                print(f"Error running allfour.py: {str(e)}")
                raise

            # Check for final_outputs directory and find the latest run folder
            final_outputs_dir = os.path.join(OUTPUT_DIR, "final_outputs")
            if os.path.exists(final_outputs_dir) and os.path.isdir(final_outputs_dir):
                # Get all run folders in final_outputs
                run_folders = [f for f in os.listdir(final_outputs_dir) 
                              if os.path.isdir(os.path.join(final_outputs_dir, f)) and f.startswith("run_")]
                
                if run_folders:
                    # Sort by creation time (newest first)
                    run_folders.sort(key=lambda x: os.path.getctime(os.path.join(final_outputs_dir, x)), reverse=True)
                    latest_run_folder = run_folders[0]
                    latest_run_path = os.path.join(final_outputs_dir, latest_run_folder)
                    
                    # Get both image and video files from the latest run folder
                    if os.path.exists(latest_run_path):
                        all_files = [f for f in os.listdir(latest_run_path) 
                                 if os.path.isfile(os.path.join(latest_run_path, f))]
                        
                        # Separate images and videos
                        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                        video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.webm'))]
                        
                        # Sort each type by modification time
                        image_files.sort(key=lambda x: os.path.getmtime(os.path.join(latest_run_path, x)), reverse=True)
                        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(latest_run_path, x)), reverse=True)
                        
                        # Take top 3 of each type
                        top_images = image_files  # Changed from image_files[:3]
                        top_videos = video_files  # Changed from video_files[:3]
                        
                        # Combine the results
                        meme_files = [f"http://127.0.0.1:5000/outputs/final_outputs/{latest_run_folder}/{f}" 
                                    for f in (top_images + top_videos)]

            # If no files found in the final_outputs, fall back to the main output directory
            if not meme_files:
                all_files = [f for f in os.listdir(OUTPUT_DIR) 
                         if os.path.isfile(os.path.join(OUTPUT_DIR, f))]
                
                # Separate images and videos
                image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.webm'))]
                
                # Sort each type by modification time
                image_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
                video_files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
                
                # Take top 3 of each type
                top_images = image_files  # Changed from image_files[:3]
                top_videos = video_files  # Changed from video_files[:3]
                
                # Combine the results
                meme_files = [f"http://127.0.0.1:5000/outputs/{f}" for f in (top_images + top_videos)]

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


@app.route('/outputs/final_outputs/<path:filepath>')
def serve_final_output(filepath):
    """
    Serve files from the final_outputs directory and its subdirectories.
    The filepath might contain subdirectories like 'run_20230928_123456/meme.jpg'
    """
    # Split the filepath into parts
    parts = filepath.split('/')
    if len(parts) >= 2:
        # The first part is the run folder, the rest is the file path within it
        run_folder = parts[0]
        filename = '/'.join(parts[1:])
        final_outputs_dir = os.path.join(OUTPUT_DIR, "final_outputs")
        run_folder_path = os.path.join(final_outputs_dir, run_folder)
        return send_from_directory(run_folder_path, filename)
    return "File not found", 404


@app.route('/get_memes')
def get_memes():
    # Reuse the get_all_memes logic for consistency
    return get_all_memes()


@app.route('/get_all_memes')
def get_all_memes():
    # Check all output directories for memes
    all_memes = []
    
    # Check final_outputs directory (for video/YouTube results)
    final_outputs_dir = os.path.join(OUTPUT_DIR, "final_outputs")
    if os.path.exists(final_outputs_dir) and os.path.isdir(final_outputs_dir):
        # Get all run folders in final_outputs
        run_folders = [f for f in os.listdir(final_outputs_dir) 
                      if os.path.isdir(os.path.join(final_outputs_dir, f)) and f.startswith("run_")]
        
        if run_folders:
            # Sort by creation time (newest first)
            run_folders.sort(key=lambda x: os.path.getctime(os.path.join(final_outputs_dir, x)), reverse=True)
            latest_run_folder = run_folders[0]
            latest_run_path = os.path.join(final_outputs_dir, latest_run_folder)
            
            # Get image files from the latest run folder
            if os.path.exists(latest_run_path):
                files = [f for f in os.listdir(latest_run_path) 
                       if os.path.isfile(os.path.join(latest_run_path, f)) and 
                       f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm'))]
                
                for f in files:
                    file_path = os.path.join(latest_run_path, f)
                    mtime = os.path.getmtime(file_path)
                    url = f"http://127.0.0.1:5000/outputs/final_outputs/{latest_run_folder}/{f}"
                    all_memes.append((url, mtime))
    
    # Check main output directory
    if os.path.exists(OUTPUT_DIR):
        main_files = [f for f in os.listdir(OUTPUT_DIR) 
                     if os.path.isfile(os.path.join(OUTPUT_DIR, f)) 
                     and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm'))]
        
        for f in main_files:
            file_path = os.path.join(OUTPUT_DIR, f)
            mtime = os.path.getmtime(file_path)
            url = f"http://127.0.0.1:5000/outputs/{f}"
            all_memes.append((url, mtime))
    
    # Check photo memes directory
    if os.path.exists(PHOTO_OUTPUT_DIR):
        photo_files = [f for f in os.listdir(PHOTO_OUTPUT_DIR) 
                      if os.path.isfile(os.path.join(PHOTO_OUTPUT_DIR, f)) 
                      and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        for f in photo_files:
            file_path = os.path.join(PHOTO_OUTPUT_DIR, f)
            mtime = os.path.getmtime(file_path)
            url = f"http://127.0.0.1:5000/outputs/photo_memes/{f}"
            all_memes.append((url, mtime))
    
    # Sort by modification time (newest first)
    all_memes.sort(key=lambda x: x[1], reverse=True)
    
    # Separate images and videos
    images = [(url, time) for url, time in all_memes if not url.lower().endswith(('.mp4', '.webm'))]
    videos = [(url, time) for url, time in all_memes if url.lower().endswith(('.mp4', '.webm'))]
    
    # Take top 3 of each type
    top_images = [url for url, _ in images[:]]
    top_videos = [url for url, _ in videos[:]]
    
    # Combine and return both types
    top_memes = top_images + top_videos
    
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
