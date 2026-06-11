import os
from typing import List
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

# 1. Create a global variable but DO NOT load the model yet
_model = None  

def get_model():
    """Only loads the model into memory the very first time it is needed."""
    global _model
    if _model is None:
        print(f"\n--> Booting up local AI engine ({MODEL_NAME})...")
        _model = SentenceTransformer(MODEL_NAME)
        print("--> AI Engine ready!\n")
    return _model

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates semantic vector embeddings completely locally."""
    if not texts:
        return []
    
    # 2. Fetch the model (will load it if it's the first run)
    model = get_model()
    
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

def create_query_embedding(query: str) -> List[float]:
    return create_embeddings([query])[0]