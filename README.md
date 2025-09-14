# Meme Generator

A Python project that extracts funny moments from videos and generates memes automatically.  
This is a hackathon MVP for creating both **photo memes** and **video clips** from humorous segments in videos.

---

## Features
- Extract video transcript with timestamps
- Detect potentially funny moments (keywords, laughter, pauses)
- Generate image-based memes
- Clip funny video segments for video memes

---

## Project Structure
Meme Generator/
│── app.py # main app entry point
│── test.py # test scripts
│── processPipeline.py # transcript extraction and processing pipeline
│── verbalProcess/ # code for transcript and text processing
│── visualProcess/ # code for video/image processing
│── requirements.txt # Python dependencies
│── README.md # this file
│── .gitignore # ignored files/folders


---

## Setup & Installation

# Clone the repo:
git clone https://github.com/<GITHUB_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>

# Create a virtual environment and activate it:
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies:
pip install -r requirements.txt
