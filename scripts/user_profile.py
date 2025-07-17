# scripts/3_user_profile.py

import os
import numpy as np

# -------- Configuration --------
EMB_DIR = "embeddings"
USER_CLOTH_EMB = os.path.join(EMB_DIR, "user_clothes.npy")   # user wearing cloth-only images
USER_MODEL_EMB = os.path.join(EMB_DIR, "user_images.npy")   # user images with model wearing cloth
USER_PROFILE_PATH = os.path.join(EMB_DIR, "user_profile.npy")

# -------- Load embeddings --------
# Ensure both files exist
if not os.path.exists(USER_CLOTH_EMB) or not os.path.exists(USER_MODEL_EMB):
    raise FileNotFoundError(
        f"Make sure both user cloth embeddings ({USER_CLOTH_EMB}) and model embeddings ({USER_MODEL_EMB}) exist."
    )

cloth_emb = np.load(USER_CLOTH_EMB)    # shape: (M, D1)
model_emb = np.load(USER_MODEL_EMB)    # shape: (M, D2)

if cloth_emb.shape[0] != model_emb.shape[0]:
    raise ValueError(
        f"Embedding count mismatch: cloth {cloth_emb.shape[0]} vs model {model_emb.shape[0]}"
    )

# -------- Concatenate embeddings --------
# Combine cloth and model embeddings for each item
combined = np.concatenate([cloth_emb, model_emb], axis=1).astype('float32')

# -------- Compute user profile --------
# e.g., mean vector across all items
user_profile = np.mean(combined, axis=0)

# -------- Save profile --------
os.makedirs(EMB_DIR, exist_ok=True)
np.save(USER_PROFILE_PATH, user_profile)
print(
    f"Saved user profile embedding of dimension {user_profile.shape[0]} to {USER_PROFILE_PATH}"
)
