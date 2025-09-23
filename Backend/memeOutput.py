import os
import json
import cv2
from PIL import Image, ImageDraw, ImageFont
import textwrap
import subprocess

# Paths
OUTPUTS_DIR = "outputs"
FRAMES_DIR = os.path.join(OUTPUTS_DIR, "frames")
CLIPS_DIR = os.path.join(OUTPUTS_DIR, "clips")
FINAL_DIR = os.path.join(OUTPUTS_DIR, "final_outputs")
MEME_JSON = os.path.join(OUTPUTS_DIR, "meme_moments.json")
FONT_PATH = os.path.join("fonts", "Impact.ttf")  # make sure font file exists

os.makedirs(FINAL_DIR, exist_ok=True)

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
    font_size = int(H * 0.15)  # start big
    while font_size > 10:
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()
            break

        # Use textbbox instead of textsize
        bbox = draw.textbbox((0, 0), caption.upper(), font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        if w <= W * 0.95:
            break
        font_size -= 2

    # ✅ Fixed text wrapping (avoid division by zero / unstable calc)
    avg_char_width = font_size * 0.2
    max_chars = max(10, int(W / avg_char_width))  # at least 10 chars
    wrapped = textwrap.fill(caption.upper(), width=max_chars)
    lines = wrapped.split("\n")

    # Draw text at top with outline
    y = 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - w) / 2
        draw.text((x, y), line, font=font,
                  fill="white", stroke_width=8, stroke_fill="black")
        y += h + 5

    img.save(output_path)
    print(f"[✔] Saved image meme: {output_path}")


# ==============================
# Add caption to video and keep audio
# ==============================
def add_caption_to_video(video_path, caption, output_path):
    import tempfile

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[❌] Could not open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    temp_output = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    out = cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = max(2, int(width / 400))

    # Wrap caption to multiple lines based on video width
    max_chars_per_line = width // 25
    wrapped = textwrap.fill(caption.upper(), width=max_chars_per_line)
    lines = wrapped.split("\n")

    # Dynamically calculate font scale so widest line fits
    longest_line = max(lines, key=len)
    for fs in reversed(range(1, 500)):  # try font scales from big to small
        (text_w, text_h), _ = cv2.getTextSize(longest_line, font, fs / 100, thickness)
        if text_w <= width - 20:  # 10px margin on each side
            font_scale = fs / 100
            break

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        y = 50  # start a little below top
        for line in lines:
            (text_w, text_h), _ = cv2.getTextSize(line, font, font_scale, thickness)
            x = (width - text_w) // 2

            # Draw black outline
            cv2.putText(frame, line, (x, y), font, font_scale,
                        (0, 0, 0), thickness + 4, cv2.LINE_AA)
            # Draw white text
            cv2.putText(frame, line, (x, y), font, font_scale,
                        (255, 255, 255), thickness, cv2.LINE_AA)
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
        output_img = os.path.join(FINAL_DIR, f"final_meme_{i}.jpg")
        add_caption_to_image(frame_file, caption, output_img)

    # Video
    clip_file = os.path.join(CLIPS_DIR, f"meme_{i}.mp4")
    if os.path.exists(clip_file):
        output_vid = os.path.join(FINAL_DIR, f"final_meme_{i}.mp4")
        add_caption_to_video(clip_file, caption, output_vid)
       