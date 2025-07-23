
import os
from huggingface_hub import hf_hub_download

# Define the directory where models will be saved
download_dir = "checkpoints"
os.makedirs(download_dir, exist_ok=True)

# 1. Download Stable Diffusion 1.4 Checkpoint (main model for this repo)
print("Downloading Stable Diffusion 1.4 checkpoint...")
sd_repo_id = "runwayml/stable-diffusion-v1-4"
sd_filename = "sd-v1-4.ckpt" # This repo often uses .ckpt
hf_hub_download(repo_id=sd_repo_id, filename=sd_filename, local_dir=download_dir, local_dir_use_symlinks=False)
print(f"Downloaded {sd_filename} to {download_dir}")

# 2. Download ControlNet 1.4 Pose Model
print("Downloading ControlNet 1.4 Pose model...")
cn_repo_id = "lllyasviel/ControlNet-v1-1" # ControlNet v1.1 repo contain
cn_pose_filename = "control_sd14_pose.pth" # This exact filename is specified in SD-VITON
hf_hub_download(repo_id=cn_repo_id, filename=cn_pose_filename, local_dir=download_dir, local_dir_use_symlinks=False)
print(f"Downloaded {cn_pose_filename} to {download_dir}")

print("Downloading ControlNet 1.4 Segmentation model...")
cn_seg_filename = "control_sd14_segmentation.pth" 
hf_hub_download(repo_id=cn_repo_id, filename=cn_seg_filename, local_dir=download_dir, local_dir_use_symlinks=False)
print(f"Downloaded {cn_seg_filename} to {download_dir}")

print("\nAll required models downloaded to the 'checkpoints' directory.")

