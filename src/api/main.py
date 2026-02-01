"""Production FastAPI backend."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import uvicorn
from src.core.rag_chain import RAGAssistant
from src.ingestion.loader import DocumentIngester
from src.core.vectorstore import VectorStoreManager

app = FastAPI(title="RAG Assistant API", version="1.0.0")

rag = RAGAssistant()
ingester = DocumentIngester()

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    status: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        result = await rag.query(request.question, request.session_id)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_documents(file_paths: List[str]):
    try:
        documents = ingester.process_documents(file_paths)
        vs = VectorStoreManager()
        if vs.load_index():
            vs.add_documents(documents)
        else:
            vs.create_index(documents)
        return {"status": "success", "documents_processed": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=False)

