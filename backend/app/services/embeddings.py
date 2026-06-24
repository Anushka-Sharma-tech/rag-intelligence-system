import os
import requests
from typing import List
from fastapi import HTTPException

# Grab the free token from Railway's environment
HF_TOKEN = os.getenv("HF_TOKEN")

# This is the exact same model you used locally, but hosted on Hugging Face's free servers!
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-small-en-v1.5"

def create_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
        
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        # We use wait_for_model=True in case HF needs a few seconds to wake the free model up
        response = requests.post(
            API_URL, 
            headers=headers, 
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        response.raise_for_status() # Check for HTTP errors
        return response.json()
        
    except Exception as e:
        print(f"Hugging Face API failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to generate embeddings via Hugging Face. Check API token."
        )

def create_query_embedding(query: str) -> List[float]:
    return create_embeddings([query])[0]
