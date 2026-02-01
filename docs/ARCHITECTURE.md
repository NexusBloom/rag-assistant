# RAG Assistant Architecture
## System Overview
- **Pipeline**: Document → Chunk → Embed → FAISS → Retrieve → LLM → Response
- **Components**: FastAPI backend, Streamlit UI, FAISS vector store
- **Models**: GPT-4o-mini (LLM), all-MiniLM-L6-v2 (Embeddings)
