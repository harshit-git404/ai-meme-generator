# verbalProcess.py (updated)
import os
import re
import json
import glob
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
DOWNLOAD_FOLDER = "downloads"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# -----------------------------
# Global Whisper model
# -----------------------------
GLOBAL_MODEL_SIZE = "base"
logging.info(f"Loading default Whisper model ({GLOBAL_MODEL_SIZE})...")
global_model = whisper.load_model(GLOBAL_MODEL_SIZE)

# -----------------------------
# Helper: Download full video (like visualProcess)
# -----------------------------
def download_video(url, download_folder=DOWNLOAD_FOLDER):
    base_name = re.sub(r'[<>:"/\\|?*]', '_', url.split("youtu")[-1])
    filename = os.path.join(download_folder, f"{base_name}.mp4")
    counter = 1
    while os.path.exists(filename):
        filename = os.path.join(download_folder, f"{base_name}({counter}).mp4")
        counter += 1

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': filename,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logging.info(f"Downloaded full video to {filename}")
    return filename

# -----------------------------
# Helper: Download audio OR reuse existing video
# -----------------------------
def download_audio_or_get_existing(url, download_folder=DOWNLOAD_FOLDER):
    """
    If an existing full video exists, reuse it. Otherwise download audio-only.
    Returns path and boolean: True if downloaded audio-only temp file, False otherwise.
    """
    base_name = re.sub(r'[<>:"/\\|?*]', '_', url.split("youtu")[-1])
    # Check for existing mp4 (video or audio)
    pattern = os.path.join(download_folder, f"{base_name}*.mp4")
    existing = glob.glob(pattern)
    if existing:
        chosen = max(existing, key=os.path.getmtime)
        logging.info(f"Found existing downloaded file, reusing: {chosen}")
        return chosen, False

    # No existing file: download audio-only
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
    logging.info(f"Downloaded audio-only to {filename}")
    return filename, True

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
def process_verbal(input_source, model_size="base", fp16=False, keep_video=True):
    """
    Downloads full video if keep_video=True, otherwise uses audio-only.
    Returns transcription result and ensures video is saved if requested.
    """
    downloaded_temp = False

    if re.match(r'https?://(www\.)?youtu', input_source):
        if keep_video:
            # Download full video and reuse it for transcription
            file_path = download_video(input_source)
            source_type = "youtube"
        else:
            # Use original audio-only method
            file_path, downloaded_temp = download_audio_or_get_existing(input_source)
            source_type = "youtube"
    else:
        file_path = input_source  # local file
        source_type = "local"

    segments = transcribe_audio(file_path, model_size=model_size, fp16=fp16)
    result = save_transcript_json(file_path, segments, source_type)

    # Delete temporary audio-only file if needed
    if downloaded_temp:
        try:
            os.remove(file_path)
            logging.info(f"Deleted temporary audio file: {file_path}")
        except Exception as e:
            logging.warning(f"Could not delete temporary file {file_path}: {e}")

    return result

# -----------------------------
# CLI for testing
# -----------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Transcribe verbal content from video or YouTube")
    parser.add_argument("--input", type=str, required=True, help="YouTube URL or local file path")
    parser.add_argument("--model", type=str, default="base", help="Whisper model size")
    parser.add_argument("--keep-video", action="store_true", help="Download and save full video (for frame extraction)")
    args = parser.parse_args()

    result = process_verbal(args.input, model_size=args.model, keep_video=args.keep_video)
    logging.info(f"Processed {len(result['data'])} segments.")
