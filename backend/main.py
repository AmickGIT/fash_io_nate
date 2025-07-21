from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient, models       # gRPC client + models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import os
from functools import lru_cache
import numpy as np
from typing import List, Optional, Tuple


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
EXT_COLLECTION_NAME = "text_img_clothes"

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

@lru_cache(maxsize=32)
def get_profile_embedding(user_id: str) -> Tuple[List[List[float]], List[List[float]]]:
    VECTOR_DIMENSION = 2048
    def fetch_vectors(flag_key: str, flag_value: bool) -> List[List[float]]:
        flt = Filter(
            must=[FieldCondition(key=flag_key, match=MatchValue(value=flag_value))]
        )
        resp = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=flt,
            with_payload=False,
            with_vectors=True,
            limit=10_000,
        )
        pts = resp[0]
        # Extract raw vectors; each p.vector is a list[float]
        return [p.vector for p in pts]

    # 1) All bought item vectors
    positive_embeddings = fetch_vectors("bought", True)

    # 2) All not_interested item vectors
    negative_embeddings = fetch_vectors("not_interested", True)

    # If you want to ensure non-empty lists, you could fallback to a zero vector:
    # if not positive_embeddings:
    #     positive_embeddings = [[0.0] * VECTOR_DIMENSION]
    # if not negative_embeddings:
    #     negative_embeddings = [[0.0] * VECTOR_DIMENSION]

    return positive_embeddings, negative_embeddings


@app.get("/api/products")
def get_products(
    brand: Optional[List[str]] = Query(None),
    color: Optional[List[str]] = Query(None),
    sleeve: Optional[List[str]] = Query(None),
    fit: Optional[List[str]] = Query(None),
    neckline: Optional[List[str]] = Query(None),
    dress_code: Optional[List[str]] = Query(None),
    match_style: bool = Query(False),
    uniqueness: Optional[int] = Query(50),
    limit: int = Query(50, gt=0),
    offset: Optional[int] = Query(None, ge=0),
    search_query: Optional[str] = Query(None),
):
    """
    Query QDrant for products matching the filters and return image URLs.
    Supports pagination with offset and returns next_offset for 'load more'.
    If match_style is true, uses the user's profile embedding for vector search.
    """
    if(search_query):
        print(search_query)

    from qdrant_client.http import models as rest
    must_filters = []

    def build_should_filter(field, values):
        if values:
            return rest.Filter(
                should=[rest.FieldCondition(key=field, match=rest.MatchValue(value=v)) for v in values]
            )
        return None
    
    # def get_recommend_strategy(level: str):
    #     if level == "low":
    #         return RecommendStrategy.AVERAGE_VECTOR, True  # use mean vector
    #     elif level == "medium":
    #         return RecommendStrategy.AVERAGE_VECTOR, False  # use all vectors
    #     elif level == "high":
    #         return RecommendStrategy.SUM_SCORES, False
    #     else:
    #         raise ValueError("Uniqueness level must be 'low', 'medium', or 'high'")


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

    must_not_filters = [
        rest.FieldCondition(key="bought", match=rest.MatchValue(value=True)),
        rest.FieldCondition(key="not_interested", match=rest.MatchValue(value=True))
    ]
    scroll_filter = rest.Filter(must=must_filters, must_not=must_not_filters) if must_filters or must_not_filters else None
    
    try:
        if match_style:
            positive_embeddings, negative_embeddings = get_profile_embedding("default_user_id")

            if not positive_embeddings or len(positive_embeddings) == 0:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Please add at least one item to your wardrobe to get personalized recommendations."}
                )
            if uniqueness == 0:
                points = client.recommend(
                    collection_name=COLLECTION_NAME,
                    positive=positive_embeddings,   
                    negative=negative_embeddings,
                    query_filter=scroll_filter,
                    strategy=models.RecommendStrategy.AVERAGE_VECTOR,
                    limit=limit,
                    with_payload=['img_path'],
                )
            elif uniqueness == 50:
                points = client.recommend(
                    collection_name=COLLECTION_NAME,
                    positive=positive_embeddings,   
                    negative=negative_embeddings,
                    query_filter=scroll_filter,
                    strategy=models.RecommendStrategy.SUM_SCORES,
                    limit=limit,
                    with_payload=['img_path'],
                )
            elif uniqueness == 100:
                points = client.recommend(
                    collection_name=COLLECTION_NAME,
                    positive=positive_embeddings,   
                    query_filter=scroll_filter,
                    strategy=models.RecommendStrategy.SUM_SCORES,
                    limit=limit,
                    with_payload=['img_path'],
                )
            # points = client.recommend(
            #     collection_name=COLLECTION_NAME,
            #     positive=positive_embeddings,   
            #     negative=negative_embeddings,
            #     query_filter=scroll_filter,
            #     limit=limit,
            #     with_payload=True,
            # )
            
            next_offset = None  # Qdrant search does not support offset
        else:
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
                results.append({
                    "id": point.id,
                    "img_path": img_path,
                    "image_url": image_url
                })
        return {
            "items": results,
            "next_offset": next_offset
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/wardrobe")
def get_wardrobe_items(limit: int = Query(100)):
    """
    Return all items where bought=True, including their payload.
    """
    from qdrant_client.http import models as rest
    flt = rest.Filter(must=[rest.FieldCondition(key="bought", match=rest.MatchValue(value=True))])
    try:
        points, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=flt,
            with_payload=["img_path", "bought"],
            limit=limit
        )
        results = []
        for point in points:
            img_path = point.payload.get("img_path")
            if img_path:
                image_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{img_path}"
                results.append({
                    "id": point.id,
                    "img_path": img_path,
                    "image_url": image_url,
                    "payload": point.payload
                })
        return results
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/buy")
def buy_item(id: int = Body(..., embed=True)):
    """
    Set the 'bought' key of the item with the given id to True, and update the profile embedding cache.
    Return the updated wardrobe count (number of bought=True items).
    """
    client.set_payload(
        collection_name=COLLECTION_NAME,
        payload={"bought": True},
        points=[id]
    )
    get_profile_embedding.cache_clear()
    new_embedding = get_profile_embedding("default_user_id")
    print("Profile embedding updated and cached.")
    # Fetch updated wardrobe count
    from qdrant_client.http import models as rest
    flt = rest.Filter(must=[rest.FieldCondition(key="bought", match=rest.MatchValue(value=True))])
    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=flt,
        with_payload=["bought"],
        limit=10000
    )
    wardrobe_count = len(points)
    return {"success": True, "point_id": id, "wardrobe_count": wardrobe_count}

@app.post("/api/not_interested")
def mark_not_interested(id: int = Body(..., embed=True)):
    """
    Set the 'not_interested' key of the item with the given id to True.
    Return success status.
    """
    try:
        client.set_payload(
            collection_name=COLLECTION_NAME,
            payload={"not_interested": True},
            points=[id]
        )
        # Clear the profile embedding cache since user preferences changed
        get_profile_embedding.cache_clear()
        print(f"Item {id} marked as not interested.")
        return {"success": True, "point_id": id}
    except Exception as e:
        return {"error": str(e)} 