import os
import json
import glob
import openai
import re

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "meme_moments.json")

# --- Step 1: Find latest *_combined_summary.json ---
summary_files = glob.glob(os.path.join(OUTPUT_DIR, "*_combined_summary.json"))
summary_files += glob.glob(os.path.join(OUTPUT_DIR, ".*_combined_summary.json"))

if not summary_files:
    raise FileNotFoundError("❌ No combined summary JSON found in outputs/")

latest_summary = max(summary_files, key=os.path.getmtime)
print(f"[INFO] Using combined JSON: {latest_summary}")

# --- Step 2: Load combined summary JSON ---
with open(latest_summary, "r", encoding="utf-8") as f:
    combined = json.load(f)

# --- Extract verbal transcript safely ---
verbal_data = []

if isinstance(combined, dict):
    if "verbal" in combined and "data" in combined["verbal"]:
        verbal_data = combined["verbal"]["data"]
    elif combined.get("type") == "verbal" and "data" in combined:
        verbal_data = combined["data"]

elif isinstance(combined, list):
    for block in combined:
        if block.get("type") == "verbal" and "data" in block:
            verbal_data = block["data"]
            break

if not verbal_data:
    raise ValueError("❌ No 'verbal' transcript found in JSON")

# --- Step 3: Build transcript text for model ---
transcript_text = ""
for entry in verbal_data:
    transcript_text += f"[{entry['start_time']} - {entry['end_time']}] {entry['text']}\n"

# --- Step 4: Prompt for OpenRouter GPT ---
prompt = f"""
ONLY return JSON array, no explanations or markdown.
Find meme-able moments (funny, awkward, ironic, angry, frustrated).
Return JSON strictly in this format:

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

# --- Step 5: Run OpenAI (OpenRouter) model ---
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

response = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1024,
    temperature=0.7
)

raw_output = response.choices[0].message.content.strip()

# --- Step 6: Extract JSON safely ---
match = re.search(r"\[\s*{.*}\s*\]", raw_output, re.DOTALL)
if match:
    json_str = match.group(0)
    try:
        meme_moments = json.loads(json_str)
        for m in meme_moments:
            m["start"] = round(float(m["start"]), 2)
            m["end"] = round(float(m["end"]), 2)
    except json.JSONDecodeError:
        print("⚠ Failed to parse JSON, raw output:\n", json_str)
        meme_moments = []
else:
    print("⚠ No JSON found in output:\n", raw_output)
    meme_moments = []

# --- Step 7: Save results ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(meme_moments, f, indent=2, ensure_ascii=False)

print(f"✅ Meme moments saved to {OUTPUT_FILE}")
