from openai import OpenAI
from typing import List
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Batch embed texts using text-embedding-3-small.
    Processes in batches of 100 to stay within API rate limits.
    """
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=batch
        )
        all_embeddings.extend([item.embedding for item in response.data])
    return all_embeddings

def create_query_embedding(text: str) -> List[float]:
    """Embed a single query string."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=[text]
    )
    return response.data[0].embedding