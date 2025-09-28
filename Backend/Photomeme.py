# Photomeme.py
import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import uuid
import re
import requests
import json
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# --------------------------
# Directories
# --------------------------
PHOTO_OUTPUT_DIR = os.path.join(os.getcwd(), "outputs", "photo_memes")
os.makedirs(PHOTO_OUTPUT_DIR, exist_ok=True)

# --------------------------
# API Config for OpenRouter
# --------------------------
OPENROUTER_API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}"
}

# --------------------------
# Device + BLIP Model
# --------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# --------------------------
# Helpers
# --------------------------
def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "]+", 
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

def generate_blip_caption(image_path: str) -> str:
    """Generate a BLIP caption from the image."""
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = blip_processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            output_ids = blip_model.generate(**inputs)
        caption = blip_processor.decode(output_ids[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print("BLIP captioning error:", e)
        return "A funny scene"

def generate_funny_caption(prompt_text: str) -> str:
    """Generate a funny meme caption using OpenRouter API from given text."""
    prompt = f"Convert this description into a short, funny meme caption:\n{prompt_text}"

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a creative meme caption generator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(BASE_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        caption = data["choices"][0]["message"]["content"].strip()
        return remove_emojis(caption) if caption else "When life gives you memes..."
    except Exception as e:
        print("OpenRouter API error:", e)
        return "When life gives you memes..."

# --------------------------
# Meme Drawing with Black Canvas
# --------------------------
def draw_caption_with_canvas(img, caption):
    try:
        font = ImageFont.truetype("impact.ttf", size=30)
    except:
        print("Impact font not found, falling back to Arial.")
        try:
            font = ImageFont.truetype("arial.ttf", size=30)
        except:
            font = ImageFont.load_default()
            print("Arial font not found, falling back to default PIL font.")

    # Wrap text to fit image width
    draw = ImageDraw.Draw(img)
    max_width = int(img.width * 0.9)
    words = caption.split()
    lines, current_line = [], ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, _ = draw.textsize(test_line, font=font)

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Calculate text height
    line_heights = []
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            h = bbox[3] - bbox[1]
        except AttributeError:
            _, h = draw.textsize(line, font=font)
        line_heights.append(h)

    total_text_height = sum(line_heights) + (10 * (len(lines) - 1)) + 40  # padding

    # Create new canvas (black) + paste original image below
    new_img = Image.new("RGB", (img.width, total_text_height + img.height), "black")
    new_img.paste(img, (0, total_text_height))

    # Draw text on black canvas
    draw = ImageDraw.Draw(new_img)
    y = 20
    for line, h in zip(lines, line_heights):
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w, _ = draw.textsize(line, font=font)

        x = (img.width - w) // 2

        # Outline (black stroke)
        for dx in [-3, 3]:
            for dy in [-3, 3]:
                draw.text((x + dx, y + dy), line, font=font, fill="black")

        # White text
        draw.text((x, y), line, font=font, fill="white")
        y += h + 10

    return new_img

# --------------------------
# Meme Generation
# --------------------------
def generate_photo_memes(input_path, output_dir=PHOTO_OUTPUT_DIR, custom_text=None):
    try:
        img = Image.open(input_path).convert("RGB")
        base_filename = str(uuid.uuid4())
        output_filename = f"{base_filename}.png"
        output_path = os.path.join(output_dir, output_filename)

        if custom_text:
            caption = custom_text
        else:
            prompt_text = generate_blip_caption(input_path)
            caption = generate_funny_caption(prompt_text)

        img_with_caption = draw_caption_with_canvas(img, caption)
        img_with_caption.save(output_path)
        return output_path

    except Exception as e:
        print("Error in generate_photo_memes:", e)
        return None

# --------------------------
# Main (CLI + Interactive custom caption)
# --------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a meme from a photo.")
    parser.add_argument("--input", type=str, required=True, help="Path to input photo")
    args = parser.parse_args()
    # Generate once and exit (custom caption interactive flow removed)
    output_path = generate_photo_memes(args.input, PHOTO_OUTPUT_DIR)
    if output_path:
        print(f"Meme generated: {output_path}")
    else:
        print("Meme generation failed.")