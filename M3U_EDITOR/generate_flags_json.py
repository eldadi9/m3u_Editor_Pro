import os
import json

FLAGS_DIR = r"C:\Users\Master_PC\Desktop\IPtv_projects\Projects Eldad\M3u_Editor_EldadV1\flags"
OUTPUT_JSON = "flags_db.json"

def generate_flags_json():
    flags = {}
    for filename in os.listdir(FLAGS_DIR):
        if filename.lower().endswith(".png"):
            name = os.path.splitext(filename)[0]
            flags[name.lower()] = os.path.join(FLAGS_DIR, filename)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(flags, f, indent=2, ensure_ascii=False)

generate_flags_json()
