"""Configuration."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Use OPENROUTER_API_KEY from environment
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    llm_model: str = "google/gemini-flash-1.5"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    temperature: float = 0.0
    vector_store_path: str = "./vectorstore"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4

config = Config()

