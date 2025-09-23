import os
import json
import cv2
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Paths
OUTPUTS_DIR = "outputs"
FRAMES_DIR = os.path.join(OUTPUTS_DIR, "frames")
CLIPS_DIR = os.path.join(OUTPUTS_DIR, "clips")
FINAL_DIR = os.path.join(OUTPUTS_DIR, "final_outputs")
MEME_JSON = os.path.join(OUTPUTS_DIR, "meme_moments.json")

os.makedirs(FINAL_DIR, exist_ok=True)

with open(MEME_JSON, "r", encoding="utf-8") as f:
    meme_moments = json.load(f)

# ==============================
# Function to add MEME-style caption to images
# ==============================
def add_caption_to_image(image_path, caption, output_path):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    # Open image
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Load a bold font (impact-like meme font if available)
    try:
        font = ImageFont.truetype("Impact.ttf", int(H * 0.8))  # size relative to image height
    except:
        font = ImageFont.load_default()

    # Wrap caption (force uppercase)
    max_chars = 40
    wrapped = textwrap.fill(caption.upper(), width=max_chars)
    lines = wrapped.split("\n")

    # Place text at the top (like memes)
    y = 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - w) / 2

        # White text with thick black outline
        draw.text(
            (x, y),
            line,
            font=font,
            fill="#FFFAFA",
            stroke_width=10,     # outline thickness
            stroke_fill="black" # outline color
        )

        y += h + 10

    img.save(output_path)
    print(f"[✔] Saved image meme: {output_path}")

# ==============================
# Function to add MEME-style caption to videos
# ==============================
def add_caption_to_video(video_path, caption, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"[❌] Could not open video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Big meme text
    font_scale = max(1.0, width / 4900)
    thickness = max(2, width // 1000)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Wrap caption into wide lines
    max_chars = width // 19
    wrapped = textwrap.fill(caption.upper(), width=max_chars)
    lines = wrapped.split("\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Start at the top
        y = 80
        for line in lines:
            (text_w, text_h), _ = cv2.getTextSize(line, font, font_scale, thickness)
            x = (width - text_w) // 2
            # Black outline
            cv2.putText(frame, line, (x, y), font, font_scale, (0, 0, 0), thickness + 4, cv2.LINE_AA)
            # White text
            cv2.putText(frame, line, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            y += text_h + 20

        out.write(frame)

    cap.release()
    out.release()
    print(f"[✔] Saved video meme: {output_path}")

# ==============================
# Process memes
# ==============================
for i, moment in enumerate(meme_moments, start=1):
    caption = moment["suggested_caption"]

    frame_file = os.path.join(FRAMES_DIR, f"meme_{i}.jpg")
    if os.path.exists(frame_file):
        output_img = os.path.join(FINAL_DIR, f"final_meme_{i}.jpg")
        add_caption_to_image(frame_file, caption, output_img)

    clip_file = os.path.join(CLIPS_DIR, f"meme_{i}.mp4")
    if os.path.exists(clip_file):
        output_vid = os.path.join(FINAL_DIR, f"final_meme_{i}.mp4")
        add_caption_to_video(clip_file, caption, output_vid)