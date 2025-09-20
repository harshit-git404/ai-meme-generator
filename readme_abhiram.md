# AI Personal Meme Generator

AI-powered meme generator built with **FastAPI**. Upload an image, and it automatically generates a meme with a funny caption using **BLIP** and **OpenAI GPT-4o-mini**.

## Features
- Upload an image to generate a meme
- Caption enhancement via GPT
- Caption appears at the **top** of the image
- Emoji removal from captions

## Installation
```bash
git clone https://github.com/your-username/ai-personal-meme-generator.git
cd ai-personal-meme-generator
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt

ai-personal-meme-generator/
│
├─ main.py
├─ requirements.txt
├─ README.md
├─ images/          # Uploaded images
└─ generated_memes/ # Output memes
