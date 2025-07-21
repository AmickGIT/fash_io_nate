# Fashionate

A full-stack AI-powered fashion recommendation platform.

## Project Overview

Fashionate is a modern web application for personalized fashion recommendations. It features:
- **Backend:** FastAPI (Python) with Qdrant vector search for similarity and attribute-based filtering.
- **Frontend:** Next.js (React) for a fast, interactive user experience.
- **Embeddings:** Uses Sentence Transformers for text embedding and supports hybrid search (text + filters).

## Features
- Product search with natural language queries
- Attribute-based filtering (brand, color, sleeve, fit, neckline, dress code)
- Personalized recommendations ("Match my Style")
- Wardrobe management (buy, not interested)
- Responsive, modern UI

## Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Qdrant instance (local or cloud)

## Installation

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd Fashionate-Old
```

### 2. Backend Setup
```sh
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Set up your .env file with QDRANT_DB_URL and QDRANT_API_KEY
uvicorn main:app --reload
```

### 3. Frontend Setup
```sh
cd ../frontend
npm install
npm run dev
# The app will be available at http://localhost:3000
```

## Folder Structure
- `backend/` — FastAPI backend, Qdrant integration, embedding logic
- `frontend/` — Next.js frontend, React components, UI
- `embeddings/` — Precomputed embedding files
- `data/` — Data files (CSV, etc.)

## Environment Variables
- Backend: `.env` file with QDRANT_DB_URL, QDRANT_API_KEY, etc.
- Frontend: `.env.local` for any frontend secrets (optional)

## License
MIT (or your license here)

---

**For more details, see the code and comments in each folder.** 