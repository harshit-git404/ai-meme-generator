# processPipeline.py
import os
import re
import json
import logging
import shutil
from visualProcess import process_visual
from verbalProcess import process_verbal

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
# Helpers
# -----------------------------
def get_base_name(input_source):
    """Sanitize base name for local file or YouTube URL."""
    if re.match(r'https?://(www\.)?youtu', input_source):
        return re.sub(r'[<>:"/\\|?*]', '_', input_source.split("youtu")[-1])
    return os.path.splitext(os.path.basename(input_source))[0]

# -----------------------------
# Main pipeline
# -----------------------------
def process_pipeline(input_source, max_visual_scenes=None, fp16=False):
    logging.info(f"Processing input: {input_source}")

    # -----------------------------
    # Handle local copy once
    # -----------------------------
    if not re.match(r'https?://(www\.)?youtu', input_source):
        if not os.path.exists(input_source):
            raise FileNotFoundError(f"File not found: {input_source}")
        base_name = os.path.basename(input_source)
        video_path = os.path.join(DOWNLOAD_FOLDER, base_name)
        if not os.path.exists(video_path):
            shutil.copy(input_source, video_path)
            logging.info(f"Copied local file to {video_path}")
        input_source = video_path  # downstream uses this path

    # -----------------------------
    # Process
    # -----------------------------
    visual_data = process_visual(input_source, max_scenes=max_visual_scenes)
    verbal_data = process_verbal(input_source, fp16=fp16)

    # -----------------------------
    # Save combined JSON
    # -----------------------------
    base_name = get_base_name(input_source)
    combined_json_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_combined_summary.json")
    counter = 1
    while os.path.exists(combined_json_file):
        combined_json_file = os.path.join(
            OUTPUT_FOLDER, f"{base_name}_combined_summary({counter}).json"
        )
        counter += 1

    combined_result = {"visual": visual_data, "verbal": verbal_data}

    with open(combined_json_file, "w", encoding="utf-8") as f:
        json.dump(combined_result, f, indent=4, ensure_ascii=False)

    logging.info(
        f"✅ Combined summary saved to {combined_json_file} | "
        f"Visual scenes: {len(visual_data['data'])}, Verbal segments: {len(verbal_data['data'])}"
    )
    return combined_result

# -----------------------------
# CLI
# -----------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run visual + verbal processing pipeline")
    parser.add_argument("--input", type=str, required=True, help="Local file path or YouTube URL")
    parser.add_argument("--max_scenes", type=int, default=None, help="Optional: max visual scenes to process")
    parser.add_argument("--fp16", action="store_true", help="Use fp16 for Whisper transcription")
    args = parser.parse_args()

    process_pipeline(args.input, max_visual_scenes=args.max_scenes, fp16=args.fp16)
