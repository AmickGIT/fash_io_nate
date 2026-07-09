from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient, models       # gRPC client + models
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, HasIdCondition
import os
import numpy as np
from functools import lru_cache
from typing import List, Optional, Tuple
from text_embedder import TextEmbedder
from dotenv import load_dotenv


def maximal_marginal_relevance(candidate_vectors: np.ndarray, candidate_scores: np.ndarray, lambda_mult: float, k: int) -> List[int]:
    """
    Selects k items using Maximal Marginal Relevance.
    candidate_vectors: (N, D) array of embeddings for candidate items.
    candidate_scores: (N,) array of relevance scores from Qdrant.
    lambda_mult: Number between 0 and 1. 1 = pure relevance, 0 = pure diversity.
    k: Number of items to select.
    Returns: List of indices of the selected candidates.
    """
    if k >= len(candidate_vectors):
        return list(range(len(candidate_vectors)))

    # Normalize candidate_scores to [0, 1] for balanced weighting
    min_score = np.min(candidate_scores)
    max_score = np.max(candidate_scores)
    if max_score > min_score:
        norm_scores = (candidate_scores - min_score) / (max_score - min_score)
    else:
        norm_scores = candidate_scores

    # Normalize vectors to compute cosine similarity easily via dot product
    norms = np.linalg.norm(candidate_vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    norm_vectors = candidate_vectors / norms

    selected = []
    unselected = list(range(len(candidate_vectors)))
    
    # Pick first item based purely on relevance (highest score)
    first_idx = int(np.argmax(norm_scores))
    selected.append(first_idx)
    unselected.remove(first_idx)

    # Iteratively pick remaining items
    for _ in range(k - 1):
        if not unselected:
            break
            
        unselected_vectors = norm_vectors[unselected]
        selected_vectors = norm_vectors[selected]
        
        # Calculate cosine similarity between unselected items and ALREADY selected items
        # Shape: (len(unselected), len(selected))
        sims = np.dot(unselected_vectors, selected_vectors.T)
        
        # Max similarity to any already selected item (Redundancy)
        max_sims = np.max(sims, axis=1)
        
        # Calculate MMR score for each unselected item
        # lambda * relevance - (1 - lambda) * redundancy
        mmr_scores = lambda_mult * norm_scores[unselected] - (1 - lambda_mult) * max_sims
        
        # Pick the one with the highest MMR score
        best_idx_idx = int(np.argmax(mmr_scores))
        best_idx = unselected[best_idx_idx]
        
        selected.append(best_idx)
        unselected.remove(best_idx)

    return selected



app = FastAPI()



# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fash-io-nate.vercel.app",
        "http://localhost:3000",
        "https://amickcodes-fashionate.hf.space",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/")
async def root():
    return {"status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Server is running"}

load_dotenv()

QDRANT_DB_URL = os.getenv("QDRANT_DB_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION")
EXT_COLLECTION_NAME = os.getenv("EXT_COLLECTION_NAME")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# Connect to QDrant using URL and API key
client = QdrantClient(url=QDRANT_DB_URL, api_key=QDRANT_API_KEY)
text_embedder = TextEmbedder()

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
    from qdrant_client.http import models as rest
    must_filters = []

    # Cross-collection text search
    if search_query:
        text_embedding = text_embedder.encode(search_query)
        print(f"Generated embedding of shape: {text_embedding.shape}")
        # Query EXT_COLLECTION_NAME for nearest neighbors using client.search
        ext_pts = client.search(
            collection_name=EXT_COLLECTION_NAME,
            query_vector=('text', text_embedding.tolist()),
            limit=20
        )
        text_ids = [pt.id for pt in ext_pts] if ext_pts else []

        if not text_ids:
            return {
                "items": [],
                "next_offset": None,
                "error": "No matches found for search query"
            }
        
        print(f"Number of IDs from text search: {len(text_ids)}")

        # FIXED: Use HasIdCondition for point ID filtering
        text_filter = rest.Filter(
            must=[HasIdCondition(has_id=text_ids)]
        )
        must_filters.insert(0, text_filter)

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
                results = client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=models.RecommendQuery(
                        recommend=models.RecommendInput(
                            positive=positive_embeddings,
                            negative=negative_embeddings,
                            strategy=models.RecommendStrategy.AVERAGE_VECTOR,
                        )
                    ),
                    query_filter=scroll_filter,
                    limit=limit,
                    with_payload=['img_path'],
                )
                points = results.points
            else:
                skip_count = int((uniqueness / 100.0) * 15)
                fetch_k = limit * 3 + skip_count
                lambda_mult = max(0.0, min(1.0, 1.0 - (uniqueness / 100.0)))
                
                results = client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=models.RecommendQuery(
                        recommend=models.RecommendInput(
                            positive=positive_embeddings,
                            negative=negative_embeddings,
                            strategy=models.RecommendStrategy.AVERAGE_VECTOR,
                        )
                    ),
                    query_filter=scroll_filter,
                    limit=fetch_k,
                    with_payload=['img_path'],
                    with_vectors=True
                )
                raw_candidates = results.points
                candidates = raw_candidates[skip_count:]
                
                if len(candidates) <= limit:
                    points = candidates
                else:
                    candidate_vectors = np.array([pt.vector for pt in candidates])
                    candidate_scores = np.array([pt.score for pt in candidates])
                    selected_indices = maximal_marginal_relevance(candidate_vectors, candidate_scores, lambda_mult, limit)
                    points = [candidates[i] for i in selected_indices]
            
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
        import traceback
        traceback.print_exc()
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

@app.post("/api/remove_from_wardrobe")
def remove_from_wardrobe(id: int = Body(..., embed=True)):
    """
    Set the 'bought' key of the item with the given id to False, and update the profile embedding cache.
    Return the updated wardrobe count (number of bought=True items).
    """
    try:
        client.set_payload(
            collection_name=COLLECTION_NAME,
            payload={"bought": False},
            points=[id]
        )
        get_profile_embedding.cache_clear()
        print(f"Item {id} removed from wardrobe.")
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


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
    



if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting server on port: {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
