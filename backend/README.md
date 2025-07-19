# Fashionate Backend

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables as needed (optional):
   - `QDRANT_HOST` (default: localhost)
   - `QDRANT_PORT` (default: 6333)
   - `QDRANT_COLLECTION` (default: fashion_catalog)

3. Run the server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API

- `GET /api/brands` — Returns a list of brands and their counts from QDrant. 