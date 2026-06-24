import os
import requests
from typing import List
from fastapi import HTTPException

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_ID = "BAAI/bge-small-en-v1.5"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}/pipeline/feature-extraction"

def create_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Hugging Face API failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate embeddings via Hugging Face. Check API token."
        )

def create_query_embedding(query: str) -> List[float]:
    return create_embeddings([query])[0]