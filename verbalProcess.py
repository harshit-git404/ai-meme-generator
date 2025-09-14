# verbalProcess.py
import os
import re
import json
import whisper
import yt_dlp
import logging

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# -----------------------------
# Folders
# -----------------------------
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# Global Whisper model
# -----------------------------
GLOBAL_MODEL_SIZE = "base"
logging.info(f"Loading default Whisper model ({GLOBAL_MODEL_SIZE})...")
global_model = whisper.load_model(GLOBAL_MODEL_SIZE)

# -----------------------------
# Helper: Download YouTube audio
# -----------------------------
def download_audio(url, download_folder="downloads"):
    base_name = re.sub(r'[<>:"/\\|?*]', '_', url.split("youtu")[-1])
    filename = os.path.join(download_folder, f"{base_name}.mp4")
    counter = 1
    while os.path.exists(filename):
        filename = os.path.join(download_folder, f"{base_name}({counter}).mp4")
        counter += 1

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logging.info(f"Downloaded audio to {filename}")
    return filename

# -----------------------------
# Helper: Transcribe audio
# -----------------------------
def transcribe_audio(file_path, model_size="base", fp16=False):
    logging.info(f"Transcribing {file_path} using Whisper ({model_size})...")
    model = global_model if model_size == GLOBAL_MODEL_SIZE else whisper.load_model(model_size)
    result = model.transcribe(file_path, fp16=fp16)
    segments = result["segments"]
    logging.info(f"Transcription done. {len(segments)} segments detected.")
    return segments

# -----------------------------
# Save transcript JSON
# -----------------------------
def save_transcript_json(file_path, segments, source_type="local"):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    json_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_verbal_summary.json")
    counter = 1
    while os.path.exists(json_file):
        json_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_verbal_summary({counter}).json")
        counter += 1

    output = {
        "audio": file_path,
        "source": source_type,
        "type": "verbal",
        "data": [
            {"id": i + 1, "start_time": seg["start"], "end_time": seg["end"], "text": seg["text"]}
            for i, seg in enumerate(segments)
        ]
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    logging.info(f"✅ Transcript saved to {json_file}")
    return output

# -----------------------------
# Main function
# -----------------------------
def process_verbal(input_source, model_size="base", fp16=False):
    if re.match(r'https?://(www\.)?youtu', input_source):
        file_path = download_audio(input_source)
        source_type = "youtube"
    else:
        file_path = input_source  # already handled by pipeline
        source_type = "local"

    segments = transcribe_audio(file_path, model_size=model_size, fp16=fp16)
    return save_transcript_json(file_path, segments, source_type)

# -----------------------------
# CLI for testing
# -----------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe verbal content from video or YouTube")
    parser.add_argument("--input", type=str, required=True, help="YouTube URL or local file path")
    parser.add_argument("--model", type=str, default="base", help="Whisper model size")
    args = parser.parse_args()

    result = process_verbal(args.input, model_size=args.model)
    logging.info(f"Processed {len(result['data'])} segments.")
