import cv2
import numpy as np
import os
import pandas as pd
from sklearn.cluster import KMeans
from tqdm import tqdm

image_dir = "clothes_tryon_dataset/train/image/"
parse_dir = "clothes_tryon_dataset/train/image-parse-v3/"

SKIN_LABELS = [55, 28, 139, 178]  # Neck, Face, LArm, RArm

data = []

for filename in tqdm(os.listdir(image_dir)):
    if not filename.endswith(".jpg"):
        continue

    img_path = os.path.join(image_dir, filename)
    parse_path = os.path.join(parse_dir, filename.replace(".jpg", ".png"))

    person_image = cv2.imread(img_path)
    parse_map = cv2.imread(parse_path, cv2.IMREAD_GRAYSCALE)
    if person_image is None or parse_map is None:
        print(f"Skipping {filename}, file missing.")
        continue

    person_rgb = cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB)

    skin_mask = np.isin(parse_map, SKIN_LABELS).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)

    skin_pixels = cv2.bitwise_and(person_rgb, person_rgb, mask=skin_mask)
    pixels = skin_pixels.reshape(-1, 3)
    pixels = pixels[np.any(pixels != [0, 0, 0], axis=1)]

    if len(pixels) < 10:
        print(f"Not enough skin pixels for {filename}")
        continue

    skin_hsv = cv2.cvtColor(pixels.reshape(-1, 1, 3).astype(np.uint8), cv2.COLOR_RGB2HSV).reshape(-1, 3)

    kmeans = KMeans(n_clusters=1, random_state=42, n_init="auto")
    dominant_color = kmeans.fit(skin_hsv).cluster_centers_[0]
    h, s, v = dominant_color.astype(int)

    data.append({
        "filename": filename,
        "skin_H": h,
        "skin_S": s,
        "skin_V": v
    })

df = pd.DataFrame(data)
df.to_csv("dominant_skin_tones.csv", index=False)
print("Saved dominant skin HSV values to dominant_skin_tones.csv")
