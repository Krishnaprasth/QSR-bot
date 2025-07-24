from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
from retriever import VectorRetriever
from llm import LLMHandler
from cache import Cache

app = FastAPI(title="QSR CEO Query Engine")

INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
retriever = VectorRetriever(INDEX_PATH)
llm = LLMHandler()
cache = Cache()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    source_docs: Dict[str, float] = None

@app.post("/query", response_model=QueryResponse)
async def query_engine(req: QueryRequest):
    q = req.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if cache.exists(q):
        ans = cache.get(q)
        return QueryResponse(answer=ans)
    docs_and_scores = retriever.retrieve(q, top_k=5)
    contexts = [doc for doc, _ in docs_and_scores]
    answer = llm.generate_answer(q, contexts)
    cache.set(q, answer)
    return QueryResponse(answer=answer, source_docs={doc: score for doc, score in docs_and_scores})
