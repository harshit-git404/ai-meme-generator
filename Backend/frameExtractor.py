#frameExtractor.py
import os
import glob
import json
import subprocess

DOWNLOADS_DIR = "downloads"
OUTPUT_DIR = "outputs"
MEME_FILE = os.path.join(OUTPUT_DIR, "meme_moments.json")
FRAMES_DIR = os.path.join(OUTPUT_DIR, "frames")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips")

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# --- Step 1: Find latest combined summary to determine video ---
summary_files = glob.glob(os.path.join(OUTPUT_DIR, "*_combined_summary.json"))
summary_files += glob.glob(os.path.join(OUTPUT_DIR, ".*_combined_summary.json"))

if not summary_files:
    raise FileNotFoundError("❌ No combined summary JSON found in outputs/")

latest_summary = max(summary_files, key=os.path.getmtime)
base_name = os.path.basename(latest_summary).replace("_combined_summary.json", "")

# Step 2: Pick the corresponding video
possible_videos = glob.glob(os.path.join(DOWNLOADS_DIR, f"{base_name}*.mp4"))
if not possible_videos:
    raise FileNotFoundError(f"❌ No matching video found for {base_name} in downloads/")

VIDEO_FILE = max(possible_videos, key=os.path.getmtime)  # latest modified matching video
print(f"[INFO] Using video: {VIDEO_FILE}")

# --- Step 3: Load meme moments ---
with open(MEME_FILE, "r", encoding="utf-8") as f:
    meme_moments = json.load(f)

# --- Step 4: Extract frames and clips ---
for i, moment in enumerate(meme_moments):
    start = float(moment["start"])
    end = float(moment["end"])
    duration = max(1, end - start)  # at least 1 sec

    # Extract frame
    frame_path = os.path.join(FRAMES_DIR, f"meme_{i+1}.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", VIDEO_FILE,
        "-frames:v", "1", frame_path
    ])

    # Extract short clip
    clip_path = os.path.join(CLIPS_DIR, f"meme_{i+1}.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(duration), "-i", VIDEO_FILE,
        "-c", "copy", clip_path
    ])

    print(f"✅ Extracted frame {frame_path} and clip {clip_path}")

