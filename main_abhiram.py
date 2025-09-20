from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import uuid
import torch
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import re

# --------------------------
# OpenAI via OpenRouter
# --------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_API_KEY_HERE"  # replace with your key
)

app = FastAPI()

# --------------------------
# Directories
# --------------------------
IMAGE_DIR = "images"
GENERATED_DIR = "generated_memes"
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# --------------------------
# Device + Models
# --------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

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

def enhance_caption(blip_caption: str) -> str:
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative assistant that writes funny meme captions."},
                {"role": "user", "content": f"Convert this caption into a short, funny meme caption:\n{blip_caption}"}
            ]
        )
        output = response.choices[0].message.content.strip()
        return output if output else blip_caption
    except Exception as e:
        print("LLM error:", e)
        return blip_caption

def generate_meme_image(image_path: str, caption: str) -> str:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    caption = remove_emojis(caption)

    try:
        font = ImageFont.truetype("arial.ttf", size=60)
    except:
        font = ImageFont.load_default()

    max_width = image.width - 40
    words = caption.split()
    lines, current = [], ""
    for word in words:
        test_line = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)

    y = 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (image.width - w) / 2
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x+dx, y+dy), line, font=font, fill="black")
        draw.text((x, y), line, font=font, fill="white")
        y += h + 10

    meme_id = str(uuid.uuid4())
    meme_path = os.path.join(GENERATED_DIR, f"{meme_id}.jpg")
    image.save(meme_path)
    return meme_path

# --------------------------
# API Endpoint
# --------------------------
@app.post("/generate-meme")
async def generate_meme(file: UploadFile = File(...)):
    image_id = str(uuid.uuid4())
    file_path = os.path.join(IMAGE_DIR, f"{image_id}.jpg")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    image = Image.open(file_path).convert("RGB")
    blip_inputs = blip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        blip_output = blip_model.generate(**blip_inputs)
    blip_caption = blip_processor.decode(blip_output[0], skip_special_tokens=True)

    meme_caption = enhance_caption(blip_caption)
    meme_path = generate_meme_image(file_path, meme_caption)

    return JSONResponse({
        "message": "Meme generated successfully",
        "meme_path": meme_path,
        "caption": meme_caption
    })

@app.get("/")
def home():
    return {"message": "AI Personal Meme Generator API running"}
