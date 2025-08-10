#Fashion deisgner model 2 - streamlit

import streamlit as st
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os
from io import BytesIO

TOP_LABEL = 125
STYLE_WEIGHT = 1e6
CONTENT_WEIGHT = 1e0
STEPS = 300
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OUTPUT_DIR = "output_synthetic"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_image_from_file(file, shape=None, max_size=512):
    image = Image.open(file).convert('RGB')
    if max(image.size) > max_size:
        size = max_size
    else:
        size = max(image.size)

    if shape is not None:
        size = shape

    transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    image = transform(image)[:3, :, :].unsqueeze(0)
    return image

def im_convert(tensor):
    image = tensor.to("cpu").clone().detach()
    image = image.numpy().squeeze()
    image = image.transpose(1, 2, 0)
    image = image * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
    return image.clip(0, 1)

def get_next_filename(folder, prefix="output_", suffix=".jpg"):
    existing = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(suffix)]
    nums = [int(f[len(prefix):-len(suffix)]) for f in existing if f[len(prefix):-len(suffix)].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    return os.path.join(folder, f"{prefix}{next_num:03d}{suffix}")

def get_features(image, model, layers=None):
    if layers is None:
        layers = {
            '0': 'conv1_1',
            '5': 'conv2_1',
            '10': 'conv3_1',
            '19': 'conv4_1',
            '21': 'conv4_2',
            '28': 'conv5_1'
        }

    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x
    return features

def gram_matrix(tensor):
    _, d, h, w = tensor.size()
    tensor = tensor.view(d, h * w)
    return torch.mm(tensor, tensor.t())

def tensor_to_pil(tensor_img):
    img_np = (im_convert(tensor_img) * 255).astype(np.uint8)
    return Image.fromarray(img_np)

st.title("Fashion Style Transfer")

st.markdown('[Back](https://fash-io-nate.vercel.app)')

st.markdown("Upload content image, style image, and the parse mask")

content_file = st.file_uploader("Upload Content Image (person wearing top)", type=["jpg", "png"])
style_file = st.file_uploader("Upload Style Image (pattern to apply)", type=["jpg", "png"])
mask_file = st.file_uploader("Upload Segmentation Mask of the Content Image", type=["png"])

if content_file and style_file and mask_file and st.button("Generate Stylized Output"):
    with st.spinner("Processing images..."):
        content = load_image_from_file(content_file).to(DEVICE)
        style = load_image_from_file(style_file, shape=content.shape[-2:]).to(DEVICE)

        mask_bytes = np.asarray(bytearray(mask_file.read()), dtype=np.uint8)
        parse_map = cv2.imdecode(mask_bytes, cv2.IMREAD_GRAYSCALE)
        mask = (parse_map == TOP_LABEL).astype(np.uint8) * 255
        mask = cv2.resize(mask, (content.shape[3], content.shape[2]), interpolation=cv2.INTER_NEAREST)
        mask = torch.tensor(mask / 255.0).unsqueeze(0).unsqueeze(0).float().to(DEVICE)

        vgg = models.vgg19(pretrained=True).features.to(DEVICE).eval()
        for param in vgg.parameters():
            param.requires_grad_(False)

        content_features = get_features(content, vgg)
        style_features = get_features(style, vgg)
        style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

        target = content.clone().requires_grad_(True).to(DEVICE)
        optimizer = optim.Adam([target], lr=0.003)

        for i in range(STEPS):
            target_features = get_features(target, vgg)
            content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2']) ** 2)

            style_loss = 0
            for layer in style_grams:
                target_feature = target_features[layer]
                target_gram = gram_matrix(target_feature)
                style_gram = style_grams[layer]
                layer_loss = torch.mean((target_gram - style_gram) ** 2)
                b, c, h, w = target_feature.shape
                style_loss += layer_loss / (c * h * w)

            total_loss = CONTENT_WEIGHT * content_loss + STYLE_WEIGHT * style_loss
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

            if i % 50 == 0:
                #st.info(f"Step {i}, Total loss: {total_loss.item():.4f}")
                pass

        final_img = target.clone().detach()
        final_masked = final_img * mask + content * (1 - mask)

