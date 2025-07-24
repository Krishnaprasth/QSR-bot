# QSR CEO Bot – Unified Hybrid & RAG Engine

This repository provides three interfaces for querying your QSR store performance data:

1. **Hybrid NLU + Streamlit App** (`app.py`):
   - spaCy-based intent & slot extraction (`nlp_pipeline.py`)
   - pandas-based query planner (`query_planner.py`)

2. **Retrieval-Augmented Generation (RAG) Agent**:
   - `ingest.py`: Ingests `sales_data.csv` into a FAISS vector store using OpenAI Embeddings.
   - `agent.py`: Interactive CLI QA agent with LangChain.

3. **Scalable Query Engine (FastAPI)**:
   - `main.py`: HTTP API entrypoint (`/query`).
   - `retriever.py`: FAISS-based context retrieval.
   - `llm.py`: OpenAI-powered answer generation.
   - `cache.py`: Redis caching.

## Setup

1. Clone this repo and navigate:
   ```bash
   git clone <repo_url>
   cd qsr_ceo_combined
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. Add your `sales_data.csv` to the repo root.

## Streamlit App

Run:
```bash
streamlit run app.py
```
Ask questions like:
- "Which store had max Net Sales in Nov 2024?"
- "Plot trend of Outlet EBITDA for HSR"

## RAG Agent

Ingest data:
```bash
python ingest.py
```
Run agent:
```bash
python agent.py
```

## FastAPI Engine

Run locally:
```bash
uvicorn main:app --reload
```
POST to:
```http
POST http://localhost:8000/query
Content-Type: application/json

{"question": "Rank stores by Net Sales in May 2025 descending"}
```

## Docker Deployment

Build the Docker image:
```bash
docker build -t qsr-ceo-engine .
```
Run Redis:
```bash
docker run -d --name redis -p 6379:6379 redis
```
Run service:
```bash
docker run -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -v $(pwd)/sales_data.csv:/app/sales_data.csv \
  -p 8000:8000 qsr-ceo-engine
```
