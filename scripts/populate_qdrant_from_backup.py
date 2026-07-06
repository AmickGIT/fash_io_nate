import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

QDRANT_DB_URL = os.getenv("QDRANT_DB_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
EXT_COLLECTION_NAME = os.getenv("EXT_COLLECTION_NAME")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"Connecting to Qdrant at {QDRANT_DB_URL}")
qclient = QdrantClient(url=QDRANT_DB_URL, api_key=QDRANT_API_KEY, timeout=60)

# 1. Prepare Payloads
print("Preparing payloads from CSVs...")
df = pd.read_csv(os.path.join(BASE_DIR, 'misc', 'new_data.csv'))
all_urls = df['img'].tolist()
base_directory_image = "images"
all_image_urls = list(map(lambda item: f"{base_directory_image}/{item}", all_urls))

df = df.rename(columns={'img': 'img_path'})
df['img_path'] = all_image_urls

desc_df = pd.read_csv(os.path.join(BASE_DIR, 'misc', 'description.csv'))
df['description'] = desc_df['description']
df.replace("unknown", None, inplace=True)

payload_dicts = [
    {k: v for k, v in row.items() if pd.notnull(v)}
    for row in df.to_dict(orient="records")
]

for p in payload_dicts:
    p['bought'] = False
    p['not_interested'] = False

# 2. Upload Main Collection (images_and_clothes_swin)
print(f"Loading visual embeddings for {COLLECTION_NAME}...")
image_emb = np.load(os.path.join(BASE_DIR, 'embeddings', 'image_emb_swin.npy'))
cloth_emb = np.load(os.path.join(BASE_DIR, 'embeddings', 'cloth_emb_swin.npy'))
fused_emb = np.concatenate((image_emb, cloth_emb), axis=1) # 2048 dim

print(f"Recreating collection {COLLECTION_NAME}...")
qclient.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=2048, distance=models.Distance.COSINE)
)

print("Uploading visual vectors...")
records = [
    models.Record(id=idx, payload=payload_dicts[idx], vector=fused_emb[idx].tolist())
    for idx in range(len(payload_dicts))
]
qclient.upload_points(collection_name=COLLECTION_NAME, points=records, batch_size=100)

print("Creating payload indexes...")
fields_to_index = {
    "primary_color": models.PayloadSchemaType.KEYWORD,
    "brand": models.PayloadSchemaType.KEYWORD,
    "sleeve": models.PayloadSchemaType.KEYWORD,
    "fit": models.PayloadSchemaType.KEYWORD,
    "neck": models.PayloadSchemaType.KEYWORD,
    "casuality": models.PayloadSchemaType.KEYWORD,
    "pants_color": models.PayloadSchemaType.KEYWORD,
    "hair_color": models.PayloadSchemaType.KEYWORD,  
}
for field_name, field_schema in fields_to_index.items():
    qclient.create_payload_index(collection_name=COLLECTION_NAME, field_name=field_name, field_schema=field_schema)

qclient.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="description",
    field_schema=models.TextIndexParams(
        type="text",
        tokenizer=models.TokenizerType.WORD,
        min_token_len=2,
        max_token_len=10,
        lowercase=True,
    ),
)
print("Main collection upload complete!")

# 3. Upload Ext Collection (descriptions_mpnet)
print(f"\nLoading text embeddings for {EXT_COLLECTION_NAME}...")
ext_emb = np.load(os.path.join(BASE_DIR, 'embeddings', 'desc_embeddings_mpnet.npy'))

print(f"Recreating collection {EXT_COLLECTION_NAME}...")
qclient.recreate_collection(
    collection_name=EXT_COLLECTION_NAME,
    vectors_config={"text": models.VectorParams(size=768, distance=models.Distance.COSINE)}
)

print("Uploading text vectors...")
ext_records = [
    models.Record(id=idx, vector={"text": ext_emb[idx].tolist()})
    for idx in range(len(payload_dicts))
]
qclient.upload_points(collection_name=EXT_COLLECTION_NAME, points=ext_records, batch_size=100)

print("Text collection upload complete! Qdrant is fully restored.")
