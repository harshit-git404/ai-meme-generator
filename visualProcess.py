# visualProcess.py
import os
import re
import json
import cv2
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from scenedetect import ContentDetector, SceneManager, open_video
import yt_dlp
import logging

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# -----------------------------
# Folders
# -----------------------------
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Global BLIP model
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# -----------------------------
# Helper: Download YouTube video (video + audio, merged to mp4)
# -----------------------------
def download_video(url, download_folder=DOWNLOAD_FOLDER):
    base_name = re.sub(r'[<>:"/\\|?*]', '_', url.split("youtu")[-1])
    filename = os.path.join(download_folder, f"{base_name}.mp4")
    counter = 1
    # ensure unique filename
    while os.path.exists(filename):
        filename = os.path.join(download_folder, f"{base_name}({counter}).mp4")
        counter += 1

    # Request best video+audio and merge into mp4
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logging.info(f"Downloaded video (with audio) to {filename}")
    return filename

# -----------------------------
# Helper: Generate captions
# -----------------------------
def generate_captions(video_path, threshold=30.0, max_new_tokens=20, max_scenes=None):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()
    logging.info(f"Detected {len(scene_list)} scenes")

    cap = cv2.VideoCapture(video_path)
    captions = []

    scenes_to_process = scene_list if max_scenes is None else scene_list[:max_scenes]
    for i, (start, end) in enumerate(scenes_to_process):
        middle_frame = int((start.get_frames() + end.get_frames()) / 2)
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = cap.read()
        if not ret:
            continue

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        out = model.generate(**inputs, max_new_tokens=max_new_tokens)
        caption = processor.decode(out[0], skip_special_tokens=True)

        captions.append({
            "id": i + 1,
            "start_time": str(start),
            "end_time": str(end),
            "caption": caption
        })
    cap.release()

    base_name = os.path.splitext(os.path.basename(video_path))[0]
    json_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_visual_summary.json")
    counter = 1
    while os.path.exists(json_file):
        json_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_visual_summary({counter}).json")
        counter += 1

    output = {
        "video": video_path,
        "source": "youtube" if "youtu" in video_path else "local",
        "type": "visual",
        "data": captions
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    logging.info(f"✅ Captions saved to {json_file}")
    return output

# -----------------------------
# Main
# -----------------------------
def process_visual(input_source, threshold=30.0, max_new_tokens=20, max_scenes=None):
    # If input_source is a YouTube URL, download video+audio and return path.
    if re.match(r'https?://(www\.)?youtu', input_source):
        video_path = download_video(input_source)
    else:
        video_path = input_source  # already a local file path handed by pipeline

    return generate_captions(video_path, threshold, max_new_tokens, max_scenes)

# -----------------------------
# CLI for testing
# -----------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract visual captions from video")
    parser.add_argument("--input", type=str, required=True, help="YouTube URL or local file path")
    parser.add_argument("--max_scenes", type=int, default=None, help="Optional: max scenes to process")
    args = parser.parse_args()

    process_visual(args.input, max_scenes=args.max_scenes)