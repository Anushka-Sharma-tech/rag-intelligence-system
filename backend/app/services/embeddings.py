import os
from typing import List
from openai import OpenAI
from fastapi import HTTPException

# Initialize the OpenAI client (automatically uses OPENAI_API_KEY from environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Takes a list of text chunks and returns a list of embedding vectors from OpenAI.
    """
    if not texts:
        return []
        
    try:
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small" # Fast, cheap, and very low memory
        )
        # Extract the list of vectors from the API response
        return [data.embedding for data in response.data]
        
    except Exception as e:
        print(f"Embedding generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate embeddings via API. Please check the API key."
        )

def create_query_embedding(query: str) -> List[float]:
    """
    Helper function to embed a single query string.
    """
    return create_embeddings([query])[0]