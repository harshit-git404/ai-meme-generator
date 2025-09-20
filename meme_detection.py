import os
import glob
import json
import subprocess
import re

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "meme_moments.json")

# --- Step 1: Find latest *_verbal_summary.json ---
summary_files = glob.glob(os.path.join(OUTPUT_DIR, "*_verbal_summary.json"))
summary_files += glob.glob(os.path.join(OUTPUT_DIR, ".*_verbal_summary.json"))

if not summary_files:
    raise FileNotFoundError("❌ No verbal summary JSON found in outputs/")

latest_summary = max(summary_files, key=os.path.getmtime)
print(f"[INFO] Using verbal summary: {latest_summary}")

# --- Step 2: Load verbal transcript ---
with open(latest_summary, "r", encoding="utf-8") as f:
    verbal_data = json.load(f).get("data", [])

if not verbal_data:
    raise ValueError("❌ No verbal segments found in JSON")

# --- Step 3: Build transcript text for AI ---
transcript_text = ""
for entry in verbal_data:
    transcript_text += f"[{entry['start_time']} - {entry['end_time']}] {entry['text']}\n"

# --- Step 4: Build prompt ---
prompt = f"""
ONLY return JSON array, no explanations or markdown.
You are given a verbal transcript with timestamps.
Identify meme-able moments.

Rules:
1. Prioritize funny, absurd, awkward, sarcastic, or exaggerated lines.
2. If no funny parts exist, still return 1 meme-able highlight with default reason.
3. Return JSON strictly in this format:

[
  {{
    "start": "<timestamp in seconds>",
    "end": "<timestamp in seconds>",
    "reason": "<why this is meme-able>",
    "suggested_caption": "<short witty caption idea>"
  }}
]

Transcript:
{transcript_text}
"""

# --- Step 5: Run Ollama (Mistral) ---
result = subprocess.run(
    ["ollama", "run", "mistral"],
    input=prompt.encode("utf-8"),
    capture_output=True,
)

raw_output = result.stdout.decode("utf-8").strip()

# --- Step 6: Extract JSON array from model output ---
match = re.search(r"\[.*\]", raw_output, re.DOTALL)
if match:
    json_str = match.group(0)
    try:
        meme_moments = json.loads(json_str)
        # Round timestamps
        for m in meme_moments:
            m["start"] = round(float(m["start"]), 2)
            m["end"] = round(float(m["end"]), 2)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON after extraction:\n", json_str)
        meme_moments = []
else:
    print("⚠️ Could not find JSON array in output:\n", raw_output)
    meme_moments = []

# --- Step 7: Save results ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(meme_moments, f, indent=2, ensure_ascii=False)

print(f"✅ Meme moments saved to {OUTPUT_FILE}")

# --- Step 8: Call frame_extractor.py automatically if video exists ---
base_name = os.path.basename(latest_summary)
for suffix in ["_verbal_summary.json", "_combined_summary.json"]:
    if base_name.endswith(suffix):
        base_name = base_name.replace(suffix, "")
        break

video_path = os.path.join("downloads", base_name + ".mp4")
if os.path.exists(video_path):
    print("[INFO] Running frame extractor...")
    subprocess.run(["python", "frame_extractor.py"])
else:
    print(f"[WARN] Video not found, skipping frame extraction: {video_path}")
