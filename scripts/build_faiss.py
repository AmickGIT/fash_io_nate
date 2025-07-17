# scripts/2_build_faiss.py

import os
import numpy as np
import pandas as pd
import faiss

# -------- Configuration --------
EMB_DIR      = "embeddings"
CLOTH_EMB    = os.path.join(EMB_DIR, "catalog_clothes.npy")       # embeddings of cloth-only images
MODEL_EMB    = os.path.join(EMB_DIR, "catalog_images.npy")       # embeddings of model-wearing images
CATALOG_CSV  = "catalog.csv"                                    # catalog items list
INDEX_PATH   = os.path.join(EMB_DIR, "faiss_catalog.index")     # path to save FAISS index

# Number of top recommendations to retrieve
top_k = 10

# -------- Load embeddings and metadata --------
print("Loading embeddings...")
cloth_emb = np.load(CLOTH_EMB)    # shape: (N, D1)
model_emb = np.load(MODEL_EMB)    # shape: (N, D2)

assert cloth_emb.shape[0] == model_emb.shape[0], "Embedding count mismatch"

# Concatenate along feature axis
total_emb = np.concatenate([cloth_emb, model_emb], axis=1).astype('float32')
print(f"Concatenated embeddings shape: {total_emb.shape}")

# -------- Build FAISS index --------
print("Building FAISS index...")
dim = total_emb.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(total_emb)

# Save index to disk
faiss.write_index(index, INDEX_PATH)
print(f"FAISS index built and saved to {INDEX_PATH}")

# -------- Example: Search for similar items to a query embedding --------
# Here, we use a user profile vector as query: load from embeddings/user_profile.npy
user_profile_path = os.path.join(EMB_DIR, "user_profile.npy")
if os.path.exists(user_profile_path):
    query_emb = np.load(user_profile_path).astype('float32')  # shape: (D,)
    query_emb = np.expand_dims(query_emb, axis=0)
    print("Searching FAISS for top_k similar items...")
    distances, indices = index.search(query_emb, top_k)
    # Load catalog metadata
    df_catalog = pd.read_csv(CATALOG_CSV)
    results = df_catalog.iloc[indices[0]]
    print(results[['img', 'brand', 'sleeve', 'neckline', 'primary_color']])
else:
    print(f"User profile embeddings not found at {user_profile_path}. Build user profile first.")
