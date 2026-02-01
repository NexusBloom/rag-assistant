"""FAISS vector store with persistence."""
from typing import List, Optional
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from src.utils.config import config

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.store_path = Path(config.vector_store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore: Optional[FAISS] = None
    
    def create_index(self, documents: List[Document]) -> FAISS:
        self.vectorstore = FAISS.from_documents(documents=documents, embedding=self.embeddings)
        self.vectorstore.save_local(str(self.store_path))
        return self.vectorstore
    
    def load_index(self) -> Optional[FAISS]:
        try:
            if not (self.store_path / "index.faiss").exists():
                return None
            self.vectorstore = FAISS.load_local(str(self.store_path), self.embeddings, allow_dangerous_deserialization=True)
            return self.vectorstore
        except Exception:
            return None
    
    def add_documents(self, documents: List[Document]):
        """Add documents to existing index."""
        if self.vectorstore is None:
            self.load_index()
        
        if self.vectorstore is None:
            return self.create_index(documents)
        
        self.vectorstore.add_documents(documents)
        self.vectorstore.save_local(str(self.store_path))
    
    def get_retriever(self, search_k: int = None):
        if self.vectorstore is None:
            self.load_index()
        if self.vectorstore is None:
            raise ValueError("No vector store available")
        return self.vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": search_k or config.top_k})

