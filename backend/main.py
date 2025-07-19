from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Optional
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
    brand: Optional[List[str]] = Query(None),
    color: Optional[List[str]] = Query(None),
    sleeve: Optional[List[str]] = Query(None),
    fit: Optional[List[str]] = Query(None),
    neckline: Optional[List[str]] = Query(None),
    dress_code: Optional[List[str]] = Query(None),
    limit: int = Query(50, gt=0),
    offset: Optional[int] = Query(None, ge=0),  # <-- new!
):
    """
    Query QDrant for products matching the filters and return image URLs.
    Supports pagination with offset and returns next_offset for 'load more'.
    """
    from qdrant_client.http import models as rest
    must_filters = []

    def build_should_filter(field, values):
        if values:
            return rest.Filter(
                should=[rest.FieldCondition(key=field, match=rest.MatchValue(value=v)) for v in values]
            )
        return None

    for field, values in [
        ("brand", brand),
        ("primary_color", color),
        ("sleeve", sleeve),
        ("fit", fit),
        ("neck", neckline),
        ("casuality", dress_code),
    ]:
        should_filter = build_should_filter(field, values)
        if should_filter:
            must_filters.append(should_filter)

    must_not_filters = [rest.FieldCondition(key="bought", match=rest.MatchValue(value=True))]
    scroll_filter = rest.Filter(must=must_filters, must_not=must_not_filters) if must_filters or must_not_filters else None

    try:
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=scroll_filter,
            with_payload=["img_path"],
            limit=limit,
            offset=offset
        )
        results = []
        for point in points:
            img_path = point.payload.get("img_path")
            if img_path:
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{img_path}"
                results.append({"img_path": img_path, "image_url": image_url})
        return {
            "items": results,
            "next_offset": next_offset
        }
    except Exception as e:
        return {"error": str(e)} 