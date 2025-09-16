import os
import json
import subprocess

VIDEO_FILE = "downloads/.be_mlKsC7X2t0g_si=oQxNMb49LG7Isxz8.mp4"  # Change to your video
MEME_FILE = "outputs/meme_moments.json"
FRAMES_DIR = "outputs/frames"
CLIPS_DIR = "outputs/clips"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

# Load meme moments
with open(MEME_FILE, "r", encoding="utf-8") as f:
    meme_moments = json.load(f)

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
