#memeOutput
import os
import json
import cv2
from PIL import Image, ImageDraw, ImageFont
import textwrap
import subprocess
import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
FRAMES_DIR = os.path.join(OUTPUTS_DIR, "frames")
CLIPS_DIR = os.path.join(OUTPUTS_DIR, "clips")
FINAL_DIR = os.path.join(OUTPUTS_DIR, "final_outputs")
MEME_JSON = os.path.join(OUTPUTS_DIR, "meme_moments.json")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "impact.ttf")  # lowercase name for safety

# Make unique folder for this run
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DIR = os.path.join(FINAL_DIR, f"run_{timestamp}")
os.makedirs(RUN_DIR, exist_ok=True)

# Load memes
with open(MEME_JSON, "r", encoding="utf-8") as f:
    meme_moments = json.load(f)

# ==============================
# Add caption to images
# ==============================
def add_caption_to_image(image_path, caption, output_path):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Determine max font size to fit width
    font_size = int(H * 0.15)
    while font_size > 10:
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            raise RuntimeError(f"Could not load Impact font at {FONT_PATH}: {e}")
        bbox = draw.textbbox((0, 0), caption.upper(), font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= W * 0.95:
            break
        font_size -= 2

    # Wrap text
    max_chars = int(len(caption) * W / w) if w else 40
    wrapped = textwrap.fill(caption.upper(), width=max_chars)
    lines = wrapped.split("\n")

    y = 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - w) / 2
        draw.text((x, y), line, font=font, fill="white", stroke_width=8, stroke_fill="black")
        y += h + 5

    img.save(output_path)
    print(f"[✔] Saved image meme: {output_path}")

# ==============================
# Add caption to video
# ==============================
def add_caption_to_video(video_path, caption, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[❌] Could not open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    temp_output = os.path.join(RUN_DIR, "temp_video.mp4")
    out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = max(2, int(width / 400))

    max_chars_per_line = width // 25
    wrapped = textwrap.fill(caption.upper(), width=max_chars_per_line)
    lines = wrapped.split("\n")

    longest_line = max(lines, key=len)
    for fs in reversed(range(1, 500)):
        (text_w, text_h), _ = cv2.getTextSize(longest_line, font, fs / 100, thickness)
        if text_w <= width - 20:
            font_scale = fs / 100
            break

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        y = 50
        for line in lines:
            (text_w, text_h), _ = cv2.getTextSize(line, font, font_scale, thickness)
            x = (width - text_w) // 2
            cv2.putText(frame, line, (x, y), font, font_scale, (0,0,0), thickness + 4, cv2.LINE_AA)
            cv2.putText(frame, line, (x, y), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)
            y += text_h + 15

        out.write(frame)

    cap.release()
    out.release()

    # Add original audio using ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_output,
        "-i", video_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(temp_output)

    print(f"[✔] Saved video meme with audio: {output_path}")

# ==============================
# Process all memes
# ==============================
for i, moment in enumerate(meme_moments, start=1):
    caption = moment["suggested_caption"]

    # Image
    frame_file = os.path.join(FRAMES_DIR, f"meme_{i}.jpg")
    if os.path.exists(frame_file):
        output_img = os.path.join(RUN_DIR, f"final_meme_{i}.jpg")
        add_caption_to_image(frame_file, caption, output_img)

    # Video
    clip_file = os.path.join(CLIPS_DIR, f"meme_{i}.mp4")
    if os.path.exists(clip_file):
        output_vid = os.path.join(RUN_DIR, f"final_meme_{i}.mp4")
        add_caption_to_video(clip_file, caption, output_vid)
