# scripts/4_search_faiss.py

import os
import numpy as np
import pandas as pd
import faiss

# -------- Configuration --------
EMB_DIR      = "embeddings"
CATALOG_CSV  = "catalog.csv"
INDEX_PATH   = os.path.join(EMB_DIR, "faiss_catalog.index")
USER_PROFILE = os.path.join(EMB_DIR, "user_profile.npy")

# Number of top recommendations to retrieve
top_k = 10

# -------- Load FAISS Index --------
if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")

index = faiss.read_index(INDEX_PATH)

# -------- Load Query Embedding --------
if not os.path.exists(USER_PROFILE):
    raise FileNotFoundError(f"User profile not found at {USER_PROFILE}")

query_emb = np.load(USER_PROFILE).astype('float32')  # shape: (D,)
query_emb = np.expand_dims(query_emb, axis=0)        # shape: (1, D)

# -------- Search FAISS --------
print("Searching FAISS for top_k similar items...")
distances, indices = index.search(query_emb, top_k)

# -------- Retrieve Catalog Items --------
df_catalog = pd.read_csv(CATALOG_CSV)
results = df_catalog.iloc[indices[0]]

# Display top results
print(results[['img', 'brand', 'sleeve', 'neckline', 'primary_color']])
