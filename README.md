# FASHIONATE

> An AI-powered full-stack virtual fashion styling and recommendation platform.

Our project blends the following into a unified web platform that understands your fashion sense, recommends what suits your skin tone.

---

## Features

### 1. Skin Color Compatibility Model
Recommends clothing colors that suit your skin tone.
- Uses segmentation to extract skin regions (face, arms, neck).
- Dominant skin tone is detected in HSV space via KMeans.
- A trained ANN predicts whether a skin–clothing color pair is a good match.

---

### 2. Fashion Designer Model – Part A (Attribute Recombination)
Recombines garment attributes to design novel outfit ideas.
- Attributes: sleeve type, neck type, color, fit.
- ANN trained to interpolate between attribute vectors of two garments.
- Output is a new blended garment style (e.g., sleeve from one, color from another).

---

### 3. Fashion Designer Model – Part B (Neural Style Transfer)
Transfers the **style** (e.g. print, texture) of one garment onto the **structure** (fit, shape) of another.
- Uses pre-trained **VGG19**.
- Balances content and style loss to generate novel clothing designs.

---

### 4. Dataset & Embedding Vectors
- Garment metadata (sleeve, neck, color, fit, etc.) enriched via a Vision-Language Model (Qwen-2.5-VL).
- Images embedded using Swin Transformer (2048-dim visual vector).
- Descriptions embedded using `all-mpnet-base-v2` (Sentence Transformers).

---

### 5. Recommendation System
- Learns user style using "Bought" and "Not Interested" tags.
- Uses **HNSW + MMR** for diverse and relevant results.
- Uniqueness Bar adjusts recommendation diversity using Maximal Marginal Relevance.

---

### 6. Natural Language Search
- Query clothes by natural phrases like “Red sleeveless party wear”.
- Uses Qwen-2B + SentenceTransformer to encode garment metadata and text descriptions.
- Searches top-k matches with **FAISS**.

---

## Other models, not implemented in web package:
### Virtual Try-On (SD-VITON)
- Squeezing-averse virtual try-on using **Sequential Deformation (SD-VITON)**.
- Pipeline:
  - Person image + clothing + pose + segmentation + DensePose
  - Condition Generator: UNet with TVOB and TACO layers
  - Generator: SPADE GAN for realistic synthesis

#### Metrics:
| Metric   | Score     |
|----------|-----------|
| SSIM     | 0.776     |
| LPIPS    | 0.222     |
| MSE      | 0.044     |
| FID      | 52.91     |
| IS       | 3.55   |

---

## Tech Stack

- **Frontend**: ReactJS (with UI filters & search)
- **Backend**: FastAPI + Celery
- **Storage**: Supabase (image storage)
- **ML Models**: PyTorch (ANN, Style Transfer, VITON)
- **Search & Rec**: FAISS, HNSW, MMR
- **Embeddings**: Swin Transformer, SentenceTransformer

## Run inside SD-VITON Directory
### Try-On Finetuning (SD-VITON Condition Generator)
```bash
python3 train_condition.py \
  --gpu_ids 0 --Ddownx2 --Ddropout --interflowloss --occlusion \
  --tvlambda_tvob 2.0 --tvlambda_taco 2.0 \
  --dataroot ./my_data/ --data_list train_pairs.txt \
  --tocg_checkpoint checkpoints/tocg.pth \
  --batch-size 2 --save_count 1000 --G_lr 0.00015 --D_lr 0.00015 \
  --workers 4 --checkpoint_dir checkpoints/finetune_cond \
  --name finetune_cond --unfreeze_last 2 --keep_step 10000
```
### Try-On Finetuning (SD-VITON Image Generator)
```bash
  python train_generator.py --name finetune_gen -b 1 -j 0 --gpu_ids 0 --fp16 --tocg_checkpoint \
checkpoints/finetune_cond/tocg_step_007000.pth --dataroot ./my_data/ --data_list train_pairs.txt \
--occlusion --composition_mask --unfreeze_last 2 --keep_step 10000 --save_count 1000 --decay_step 5000
```
### Try-On Inference:
```bash
  python test_generator.py --gen_checkpoint ./checkpoints/toig.pth --tocg_checkpoint \
./checkpoints/tocg_step_007000.pth --gpu_ids 0 --dataroot ./my_data/ \
--data_list test_pairs.txt --test_name ctest --workers 1
```



