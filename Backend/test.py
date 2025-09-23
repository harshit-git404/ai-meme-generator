from visualProcess import process_visual
import json

# Example: YouTube URL
url = "https://youtu.be/thpF81-wrMs"
result_url = process_visual(url)

# Example: Local file
local_file = "assets/steve.mp4"
result_local = process_visual(local_file)

# Print results
print("===== YouTube Result =====")
print(json.dumps(result_url, indent=4, ensure_ascii=False))

print("\n===== Local File Result =====")
print(json.dumps(result_local, indent=4, ensure_ascii=False))
