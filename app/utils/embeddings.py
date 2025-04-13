from sentence_transformers import SentenceTransformer
from app.config import Config
from typing import List, Dict, Optional
import numpy as np

# Load local embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim embeddings

def get_embeddings(text: str) -> List[float]:
    """Generate embeddings locally"""
    return embedder.encode(text).tolist()