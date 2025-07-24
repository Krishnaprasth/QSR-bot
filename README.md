# QSR CEO Bot – Hybrid & RAG

This repository bundles two interfaces for querying your QSR store performance data:

1. **Hybrid NLU + Streamlit App** (`app.py`):
   - spaCy-based intent & slot extraction (`nlp_pipeline.py`)
   - pandas-based query planner (`query_planner.py`)

2. **Retrieval-Augmented Generation (RAG) Agent**:
   - `ingest.py`: Ingests `sales_data.csv` into FAISS using OpenAI Embeddings.
   - `agent.py`: Interactive CLI QA agent via LangChain.

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
export OPENAI_API_KEY="sk-..."
```

## Streamlit App

```bash
streamlit run app.py
```

Upload `sales_data.csv` and ask:
- "Which store had max Net Sales in Nov 2024?"
- "Show trend of Outlet EBITDA for HSR"
- "Compare Rent for KOR vs HSR in FY25"

## RAG Agent

Ingest data:

```bash
python ingest.py
```

Start agent:

```bash
python agent.py
```

Try advanced queries like:
- "Across FY 2022-23, which three stores showed the largest spikes in Other opex expenses?..."
- "If we cut Aggregator commission by 20% in Q4 2024 for KOR, how would Outlet EBITDA change?"
