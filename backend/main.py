from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List
import os

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# QDrant connection details (update as needed)
QDRANT_DB_URL = os.getenv("QDRANT_DB_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "images_and_clothes_swin")

# Connect to QDrant using URL and API key
client = QdrantClient(url=QDRANT_DB_URL, api_key=QDRANT_API_KEY)

def get_unique_field(field: str):
    try:
        scroll = client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=[field],
            limit=10000
        )
        points = scroll[0]
        value_counts = {}
        for point in points:
            value = point.payload.get(field)
            if value:
                value_counts[value] = value_counts.get(value, 0) + 1
        # Return list of {label, count} sorted by count descending
        return [
            {"label": v, "count": c}
            for v, c in sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        ]
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/dress-codes")
def get_dress_codes():
    """Fetch unique dress codes (casuality) from QDrant."""
    return get_unique_field("casuality")

@app.get("/api/colors")
def get_colors():
    """Fetch unique primary colors from QDrant."""
    return get_unique_field("primary_color")

@app.get("/api/sleeves")
def get_sleeves():
    """Fetch unique sleeve types from QDrant."""
    return get_unique_field("sleeve")

@app.get("/api/fits")
def get_fits():
    """Fetch unique fits from QDrant."""
    return get_unique_field("fit")

@app.get("/api/necklines")
def get_necklines():
    """Fetch unique necklines from QDrant."""
    return get_unique_field("neck")

@app.get("/api/brands")
def get_brands():
    """
    Query QDrant for all items, aggregate by brand, and return brand counts.
    Returns: List of {label, count}
    """
    try:
        scroll = client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=["brand"],
            limit=10000  # adjust as needed
        )
        points = scroll[0]
        brand_counts = {}
        for point in points:
            brand = point.payload.get("brand")
            if brand:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
        result = [
            {"label": brand, "count": count}
            for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        return result
    except Exception as e:
        return {"error": str(e)}

SUPABASE_URL = "https://pkraxwnlcgejwxunkeco.supabase.co"
SUPABASE_BUCKET = "imgbucket"

@app.get("/api/products")
def get_products(
    brand: str = Query(None),
    color: str = Query(None),
    sleeve: str = Query(None),
    fit: str = Query(None),
    neckline: str = Query(None),
    dress_code: str = Query(None),
    limit: int = Query(20),
):
    """
    Query QDrant for products matching the filters and return image URLs.
    Always exclude items where bought=True.
    """
    from qdrant_client.http import models as rest
    must_filters = []
    if brand:
        must_filters.append(rest.FieldCondition(key="brand", match=rest.MatchValue(value=brand)))
    if color:
        must_filters.append(rest.FieldCondition(key="primary_color", match=rest.MatchValue(value=color)))
    if sleeve:
        must_filters.append(rest.FieldCondition(key="sleeve", match=rest.MatchValue(value=sleeve)))
    if fit:
        must_filters.append(rest.FieldCondition(key="fit", match=rest.MatchValue(value=fit)))
    if neckline:
        must_filters.append(rest.FieldCondition(key="neck", match=rest.MatchValue(value=neckline)))
    if dress_code:
        must_filters.append(rest.FieldCondition(key="casuality", match=rest.MatchValue(value=dress_code)))
    must_not_filters = [rest.FieldCondition(key="bought", match=rest.MatchValue(value=True))]
    scroll_filter = rest.Filter(must=must_filters, must_not=must_not_filters) if must_filters or must_not_filters else None
    try:
        scroll = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=scroll_filter,
            with_payload=["img_path"],
            limit=limit
        )
        points = scroll[0]
        results = []
        for point in points:
            img_path = point.payload.get("img_path")
            if img_path:
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{img_path}"
                results.append({"img_path": img_path, "image_url": image_url})
        return results
    except Exception as e:
        return {"error": str(e)} 