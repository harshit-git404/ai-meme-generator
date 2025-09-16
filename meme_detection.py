import os
import glob
import json
import subprocess
import re

OUTPUT_DIR = "outputs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "meme_moments.json")

# --- Step 1: Find latest *_combined_summary.json (supports hidden .files too) ---
summary_files = glob.glob(os.path.join(OUTPUT_DIR, "*_combined_summary.json"))
summary_files += glob.glob(os.path.join(OUTPUT_DIR, ".*_combined_summary.json"))

if not summary_files:
    raise FileNotFoundError("❌ No combined summary JSON found in outputs/")

latest_summary = max(summary_files, key=os.path.getmtime)
print(f"[INFO] Using summary: {latest_summary}")

# --- Step 2: Load transcript ---
with open(latest_summary, "r", encoding="utf-8") as f:
    transcript = json.load(f)

# --- Step 3: Build prompt ---
prompt = f"""
ONLY return JSON array, no explanations or markdown.
You are given a transcript with timestamps.
Identify meme-able moments.

Rules:
1. Prioritize funny, absurd, awkward, sarcastic, or exaggerated lines.
2. If no funny parts exist, still return meme-able highlights:
   - Strong catchphrases or quotable lines
   - Ironies or contradictions
   - Emotional spikes or dramatic pauses
   - Audience reactions (laughter, applause)
3. Always return at least 1 segment if transcript is non-empty.

Return JSON in this format:

[
  {{
    "start": "<timestamp in seconds>",
    "end": "<timestamp in seconds>",
    "reason": "<why this is meme-able>",
    "suggested_caption": "<short witty caption idea>"
  }}
]

Transcript JSON:
{json.dumps(transcript, ensure_ascii=False)}
"""

# --- Step 4: Run Ollama (Mistral) ---
result = subprocess.run(
    ["ollama", "run", "mistral"],
    input=prompt.encode("utf-8"),
    capture_output=True,
)

raw_output = result.stdout.decode("utf-8").strip()

# --- Step 5: Extract JSON array from model output ---
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

# --- Step 6: Save results ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(meme_moments, f, indent=2, ensure_ascii=False)

print(f"✅ Meme moments saved to {OUTPUT_FILE}")

# --- Step 7: Call frame_extractor.py automatically ---
print("[INFO] Running frame extractor...")
subprocess.run(["python", "frame_extractor.py"])
