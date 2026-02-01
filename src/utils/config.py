"""Configuration."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    # Try these working models (check https://openrouter.ai/models for availability):
    llm_model: str = "mistralai/mixtral-8x7b-instruct"  # Popular, cheap
    # Alternatives if above fails:
    # llm_model: str = "meta-llama/llama-3-8b-instruct"
    # llm_model: str = "google/gemini-pro" 
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    temperature: float = 0.0
    vector_store_path: str = "./vectorstore"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4

config = Config()

