#customCaptions
import os
import subprocess
from memeOutput import add_caption_to_image, add_caption_to_video
import cv2

# Paths
DOWNLOADS_DIR = "downloads"
OUTPUTS_DIR = "outputs"
FRAMES_DIR = os.path.join(OUTPUTS_DIR, "custom_frames")
CLIPS_DIR = os.path.join(OUTPUTS_DIR, "custom_clips")
FINAL_DIR = os.path.join(OUTPUTS_DIR, "custom_memes")

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

# Helper: convert hh:mm:ss → seconds
def timestamp_to_seconds(ts):
    h, m, s = map(int, ts.split(":"))
    return h * 3600 + m * 60 + s

# Extract clip + frame at timestamp
def extract_custom_clip(video_path, timestamp, index):
    start_sec = timestamp_to_seconds(timestamp)
    frame_path = os.path.join(FRAMES_DIR, f"custom_{index}.jpg")
    clip_path = os.path.join(CLIPS_DIR, f"custom_{index}.mp4")

    # Extract frame
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_sec), "-i", video_path,
        "-frames:v", "1", frame_path
    ])

    # Extract 3s clip
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_sec), "-t", "3", "-i", video_path,
        "-c", "copy", clip_path
    ])

    return frame_path, clip_path

def main():
    # Find the latest video in downloads/
    videos = [f for f in os.listdir(DOWNLOADS_DIR) if f.endswith(".mp4")]
    if not videos:
        print("❌ No downloaded video found in downloads/")
        return
    video_file = max([os.path.join(DOWNLOADS_DIR, v) for v in videos], key=os.path.getmtime)
    print(f"[INFO] Using video: {video_file}")

    index = 1
    while True:
        ts = input("\n⏱ Enter timestamp (hh:mm:ss) or 'q' to quit: ").strip()
        if ts.lower() == "q":
            break
        caption = input("💬 Enter custom caption: ").strip()

        frame_path, clip_path = extract_custom_clip(video_file, ts, index)

        # Apply caption
        if os.path.exists(frame_path):
            output_img = os.path.join(FINAL_DIR, f"custom_meme_{index}.jpg")
            add_caption_to_image(frame_path, caption, output_img)

        if os.path.exists(clip_path):
            output_vid = os.path.join(FINAL_DIR, f"custom_meme_{index}.mp4")
            add_caption_to_video(clip_path, caption, output_vid)

        print(f"✅ Custom meme created for {ts}")
        index += 1

if __name__ == "__main__":
    main()