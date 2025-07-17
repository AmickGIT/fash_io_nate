# scripts/1_embed_images.py

import os
import pandas as pd
import torch
from transformers import AutoFeatureExtractor, SwinModel
from PIL import Image
import numpy as np
from tqdm import tqdm

# -------- Configuration --------
IMAGE_DIR = "./data/train/cloth"
ALL_CSV = "new_data.csv"
USER_CSV = "user_clothes.csv"
CATALOG_CSV = "catalog.csv"
EMB_DIR = "embeddings"
USER_EMB = os.path.join(EMB_DIR, "user_clothes.npy")
CATALOG_EMB = os.path.join(EMB_DIR, "catalog_clothes.npy")

# Ensure output directory exists
os.makedirs(EMB_DIR, exist_ok=True)

# -------- Load Swin Transformer Model --------
device = "cuda" if torch.cuda.is_available() else "cpu"
feature_extractor = AutoFeatureExtractor.from_pretrained("microsoft/swin-tiny-patch4-window7-224")
model = SwinModel.from_pretrained("microsoft/swin-tiny-patch4-window7-224").to(device)
EMB_DIM = model.config.hidden_size

# -------- Load and Split Data --------
df_all = pd.read_csv(ALL_CSV)
df_user = pd.read_csv(USER_CSV)
user_imgs = set(df_user["img"].tolist())
df_catalog = df_all[~df_all["img"].isin(user_imgs)].reset_index(drop=True)

# Save catalog CSV
print(f"Saving catalog with {len(df_catalog)} items to {CATALOG_CSV}")
df_catalog.to_csv(CATALOG_CSV, index=False)
print(f"User clothes: {len(df_user)} items")
print(f"Catalog clothes: {len(df_catalog)} items")

# -------- Embedding Function --------
def get_image_embedding(image_path: str) -> np.ndarray:
    """
    Load an image and return its Swin Transformer embedding.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        inputs = feature_extractor(images=img, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        if hasattr(outputs, 'last_hidden_state'):
            hidden_states = outputs.last_hidden_state
        else:
            hidden_states = outputs[0]
        emb = hidden_states.mean(dim=1).squeeze().cpu().numpy()
        return emb
    except Exception as e:
        print(f"Error embedding {image_path}: {e}")
        return np.zeros(EMB_DIM, dtype=np.float32)

# -------- Embed and Save --------
def embed_and_save(df: pd.DataFrame, output_path: str):
    """
    Embed images listed in DataFrame and save embeddings as a NumPy array.
    """
    embeddings = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Embedding to {os.path.basename(output_path)}"):
        img_file = os.path.join(IMAGE_DIR, row['img'])
        emb = get_image_embedding(img_file)
        embeddings.append(emb)
    arr = np.vstack(embeddings)
    np.save(output_path, arr)
    print(f"Saved {arr.shape[0]} embeddings of dimension {arr.shape[1]} to {output_path}")

if __name__ == "__main__":
    embed_and_save(df_user, USER_EMB)
    embed_and_save(df_catalog, CATALOG_EMB)

