#!/usr/bin/env python3
import os
import json
from supabase import create_client
from tqdm import tqdm

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
SUPABASE_URL = "https://pkraxwnlcgejwxunkeco.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrcmF4d25sY2dland4dW5rZWNvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTExNTAwMSwiZXhwIjoyMDY2NjkxMDAxfQ.gUPg3cBZqvqd9fInTiYEs-RCWppYSdbg1cytp3Bhtf4"    # service_role key for writes
BUCKET_NAME  = "train-assets"             # your Supabase storage bucket
BASE_PATH    = "data/train"               # local folder to upload

# Map table columns to your local subfolders
SUBFOLDERS = {
    "image":         "image",
    "cloth":         "cloth",
    "cloth_mask":    "cloth-mask",
    "image_parse":   "image-parse-v3",
    "openpose_img":  "openpose_img",
    "openpose_json": "openpose_json"
}

# ─── INITIALIZE CLIENT ───────────────────────────────────────────────────────────
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def upload_file(local_path: str, remote_path: str):
    """Uploads one file to Supabase Storage (with upsert)."""
    with open(local_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            remote_path,
            f,
            {"upsert": "true"}       # ensure the SDK sees upsert, and as a string
        )


def load_json(local_folder: str, filename: str):
    """Loads an OpenPose JSON file into a Python dict."""
    json_fname = filename.replace(".jpg", "_keypoints.json")
    with open(os.path.join(local_folder, json_fname), "r") as f:
        return json.load(f)

# ─── 1) UPLOAD ALL FILES ─────────────────────────────────────────────────────────
print("Uploading files to Supabase Storage...")
for col, subfolder in SUBFOLDERS.items():
    local_dir = os.path.join(BASE_PATH, subfolder)
    storage_prefix = f"train/{subfolder}"
    for fname in tqdm(os.listdir(local_dir), desc=f"Uploading {subfolder}", unit="file"):
        local_fp  = os.path.join(local_dir, fname)
        remote_fp = f"{storage_prefix}/{fname}"
        upload_file(local_fp, remote_fp)

# ─── 2) BUILD & UPSERT METADATA ─────────────────────────────────────────────────
print("Building metadata records...")
records = []
for fname in tqdm(os.listdir(os.path.join(BASE_PATH, "image")), desc="Preparing records", unit="record"):
    rec = {"filename": fname, "tags": []}
    for col, subfolder in SUBFOLDERS.items():
        if col == "openpose_json":
            # parse JSON into a dict for JSONB column
            rec[col] = load_json(os.path.join(BASE_PATH, subfolder), fname)
        else:
            # store the path under your bucket
            rec[col] = f"train/{subfolder}/{fname}"
    records.append(rec)

print("Upserting into 'train_data' table in chunks...")
chunk_size = 500
for i in range(0, len(records), chunk_size):
    supabase.table("train_data").upsert(records[i:i+chunk_size]).execute()
    print(f"  → Records {i+1}–{i+len(records[i:i+chunk_size])} done")

print("✅ All done. You can now delete your local `data/train` folder.")
