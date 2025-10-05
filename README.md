# **MemeGen AI 🤖**
MemeGen AI is an intelligent, automated pipeline that transforms personal media (YouTube videos, local video files, and photos) into high-impact, shareable memes in seconds. This project was developed for the Samsung PRISM Hackathon by Team Prometheus.

# **🎯The Problem**
The internet is fueled by memes, yet creating relevant, personal memes from your own content is a complex and time-consuming process. It requires technical skill, creative effort, and multiple tools. MemeGen AI bridges this "Content Creation Gap" by making meme generation frictionless and instantaneous.


# **✨ Our Solution**
MemeGen AI is your personal content co-pilot, an end-to-end system that handles everything from ingestion to final output.

Zero-Effort Creation: Simply provide a YouTube link, a video file, or a photo.

AI-Powered Ideation: The system automatically identifies funny, ironic, or emotionally charged moments and suggests witty captions using Large Language Models.

Multi-Format Output: Generates both static image memes (.jpg) and short, captioned video clips (.mp4).

Modern Frontend: A sleek, user-friendly web interface for easy uploading and interaction.

# **🏗️ Architecture & Workflow**
The project is built on a robust backend pipeline orchestrated by Flask, with a separate frontend built with HTML, CSS, and JavaScript.

A high-level overview of the MemeGen AI architecture, from frontend to final output. 

Video Processing Pipeline: 

1.Ingestion & Analysis (processPipeline.py): The system ingests a YouTube URL or a local video file. It uses yt-dlp to download the content and then performs transcription using OpenAI's Whisper model to get precise timestamps for the dialogue.

2.AI Ideation (memeDetection.py): The full transcript is sent to a Large Language Model (GPT-3.5-Turbo) with a carefully engineered prompt to identify "meme-able moments". The LLM returns a JSON object containing timestamps, the reasoning, and a suggested caption for each moment.

3.Asset Extraction (frameExtractor.py): Using the timestamps from the AI, FFmpeg is used to precisely extract the relevant frames (as .jpg) and video clips (as .mp4) from the source video.

4.Creation (memeOutput.py): OpenCV and Pillow are used to programmatically render the AI-suggested captions onto the extracted frames and clips, creating the final memes with the classic "Impact" font aesthetic.

# **Photo Processing Pipeline**

1.Image Understanding (Photomeme.py): A photo uploaded by the user is first analyzed by the BLIP model to generate a factual, descriptive caption (e.g., "a dog wearing sunglasses").

2.Creative Captioning (Photomeme.py): This factual description is then passed to a creative LLM (GPT-4o-mini) with a new prompt: "Turn this description into a short, funny meme caption". This two-step process ensures captions are both relevant and creative.

3.Creation (Photomeme.py): The generated caption is rendered onto a canvas above the original image using the Pillow library to create the final meme.

# **🚀 Technology Stack**
*Category*-	                                *Technologies*

Backend & Orchestration: 	                Python, Flask 

AI & Machine Learning:  	                OpenAI (GPT-3.5, GPT-4o-mini),
                                            Hugging Face Transformers (BLIP), PyTorch, Whisper 

Media Processing:      	                    FFmpeg, OpenCV, Pillow (PIL) 

Frontend: 	                                HTML5, CSS3, JavaScript

Architecture: 	                            Asynchronous Task Processing  
                                            (Threading), RESTful API 

# **⚙️ Setup and Installation**
Follow these steps to get the project running on your local machine.

*Prerequisites*
Python 3.8+
FFmpeg (must be installed and accessible from your system's PATH)
A C++ compiler (required for PySceneDetect)

*Installation*
1.Clone the repository:
Bash
git clone https://github.com/your-username/MemeGen-AI.git
cd MemeGen-AI
Create a virtual environment:

2.Create a virtual environment:
Bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3.Install the required Python packages:
Bash
pip install -r requirements.txt
(Note: You will need to create a requirements.txt file. You can generate one using pip freeze > requirements.txt in your current working environment.)

4.Set up your API Key:
Open the APIKEY.py file.
Replace the placeholder key with your actual OpenRouter API key.
openrouter_api_key = "YOUR_OPENROUTER_API_KEY"
Visit https://openrouter.ai/settings/keys for and generate an API key.

# **Running the Application**
1.Start the Flask Backend:
Open a terminal and run the main application file.
Bash
python app.py
The server will start on http://127.0.0.1:5000.

2.Launch the Frontend:
Navigate to the Frontend directory.
Open the index.html file in your web browser. You can usually do this by double-clicking the file.

You can now upload a photo, video, or YouTube link to start generating memes!

**🤝 Team Prometheus**

Abhiram Yanamadala (Team Leader)
Sai Yatin
Harshit Singh
Roshan Bilal

**DEMO Vedio**
https://drive.google.com/file/d/1xU7E0U5T_JK-tnbq8ldkMBNDGzZJwa1w/view?usp=drive_link
