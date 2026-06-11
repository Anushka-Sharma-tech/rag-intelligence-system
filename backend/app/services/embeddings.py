from fastembed import TextEmbedding
from typing import List

_model = None

def get_model():
    global _model
    if _model is None:
        print("\n--> Booting up local AI engine (BAAI/bge-small-en-v1.5)...")
        _model = TextEmbedding("BAAI/bge-small-en-v1.5")
        print("--> AI Engine ready!\n")
    return _model

def create_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    model = get_model()
    return [e.tolist() for e in model.embed(texts)]

def create_query_embedding(query: str) -> List[float]:
    return create_embeddings([query])[0]