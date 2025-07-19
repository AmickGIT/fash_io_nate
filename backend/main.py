from fastapi import FastAPI
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