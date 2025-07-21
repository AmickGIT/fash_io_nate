#Neural Style Transfer

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

def load_image(img_path, max_size=512, shape=None):
    image = Image.open(img_path).convert('RGB')
    if max(image.size) > max_size:
        size = max_size
    else:
        size = max(image.size)

    if shape is not None:
        size = shape

    in_transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])
    ])

    image = in_transform(image)[:3, :, :].unsqueeze(0)
    return image

def im_convert(tensor):
    image = tensor.to("cpu").clone().detach()
    image = image.numpy().squeeze()
    image = image.transpose(1, 2, 0)
    image = image * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
    image = image.clip(0, 1)
    return image

device = torch.device("cpu")
content = load_image("E:/Learning/AI ML/AIMS/fashion model/clothes_tryon_dataset/train/image/00042_00.jpg").to(device)
style = load_image("E:/Learning/AI ML/AIMS/fashion model/clothes_tryon_dataset/train/image/00025_00.jpg", shape=content.shape[-2:]).to(device)
vgg = models.vgg19(pretrained=True).features.to(device).eval()

parse_map = cv2.imread("E:/Learning/AI ML/AIMS/fashion model/clothes_tryon_dataset/train/image-parse-v3/00042_00.png", cv2.IMREAD_GRAYSCALE)
TOP_LABEL = 125
mask = (parse_map == TOP_LABEL).astype(np.uint8) * 255
mask = cv2.resize(mask, (content.shape[3], content.shape[2]), interpolation=cv2.INTER_NEAREST)
mask = torch.tensor(mask / 255.0).unsqueeze(0).unsqueeze(0).float()


for param in vgg.parameters():
    param.requires_grad_(False)

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
    gram = torch.mm(tensor, tensor.t())
    return gram

content_features = get_features(content, vgg)
style_features = get_features(style, vgg)

style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

target = content.clone().requires_grad_(True).to(device)


style_weight = 1e6
content_weight = 1e0

optimizer = optim.Adam([target], lr=0.003)

steps = 500
for i in range(steps):
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

    total_loss = content_weight * content_loss + style_weight * style_loss
    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()

    if i % 50 == 0:
        print(f"Step {i}, Total loss: {total_loss.item():.4f}")

final_img = target.clone().detach()
final_masked = final_img * mask + content * (1 - mask)

plt.imshow(im_convert(final_masked))
plt.title("Stylized Top")
plt.axis("off")
plt.show()


def tensor_to_pil(tensor_img):
    img_np = (im_convert(tensor_img) * 255).astype(np.uint8)
    return Image.fromarray(img_np)

output_dir = "output_synthetic"
os.makedirs(output_dir, exist_ok=True)

def get_next_filename(folder, prefix="output_", suffix=".jpg"):
    existing = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(suffix)]
    nums = [int(f[len(prefix):-len(suffix)]) for f in existing if f[len(prefix):-len(suffix)].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    return os.path.join(folder, f"{prefix}{next_num:03d}{suffix}")

final_pil_img = tensor_to_pil(final_masked)
output_path = get_next_filename(output_dir)
final_pil_img.save(output_path)
print(f"Saved stylized top-only image at: {output_path}")