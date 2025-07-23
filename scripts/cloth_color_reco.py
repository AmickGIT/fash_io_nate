import cv2
import numpy as np
import os
import csv
from sklearn.cluster import KMeans
from tqdm import tqdm

cloth_dir = "clothes_tryon_dataset/train/cloth"
mask_dir = "clothes_tryon_dataset/train/cloth-mask"

output_csv = "cloth_colors.csv"

def get_cloth_color(cloth_img_path, mask_img_path):
    cloth_img = cv2.imread(cloth_img_path)
    cloth_img = cv2.cvtColor(cloth_img, cv2.COLOR_BGR2RGB)
    mask = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)

    if cloth_img is None or mask is None:
        return None

    cloth_hsv = cv2.cvtColor(cloth_img, cv2.COLOR_RGB2HSV)
    cloth_pixels = cloth_hsv[mask > 0]

    if len(cloth_pixels) < 50:
        return None

    kmeans = KMeans(n_clusters=1, random_state=42)
    dominant_color = kmeans.fit(cloth_pixels).cluster_centers_[0]
    return dominant_color  # HSV

def get_cloth_rgb(cloth_img_path, mask_img_path):
    cloth_img = cv2.imread(cloth_img_path)
    mask = cv2.imread(mask_img_path, cv2.IMREAD_GRAYSCALE)

    if cloth_img is None or mask is None:
        return None

    cloth_rgb = cv2.cvtColor(cloth_img, cv2.COLOR_BGR2RGB)
    masked_pixels = cloth_rgb[mask > 0]

    if len(masked_pixels) < 50:
        return None

    kmeans = KMeans(n_clusters=1, random_state=42)
    dominant_rgb = kmeans.fit(masked_pixels).cluster_centers_[0]
    return dominant_rgb  # [R, G, B]

cloth_files = os.listdir(cloth_dir)
'''
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'H', 'S', 'V'])

    for fname in tqdm(cloth_files):
        if not fname.lower().endswith((".jpg", ".png")):
            continue


        cloth_path = os.path.join(cloth_dir, fname)
        mask_path = os.path.join(mask_dir, fname)

        dominant_hsv = get_cloth_color(cloth_path, mask_path)
        if dominant_hsv is not None:
            H, S, V = dominant_hsv
            writer.writerow([fname, int(H), int(S), int(V)])
'''

with open("cloth_colors_rgb.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'R', 'G', 'B'])

    for fname in tqdm(cloth_files):
        if not fname.lower().endswith((".jpg", ".png")):
            continue

        cloth_path = os.path.join(cloth_dir, fname)
        mask_path = os.path.join(mask_dir, fname)

        dominant_rgb = get_cloth_rgb(cloth_path, mask_path)
        if dominant_rgb is not None:
            R, G, B = dominant_rgb.astype(int)
            writer.writerow([fname, R, G, B])