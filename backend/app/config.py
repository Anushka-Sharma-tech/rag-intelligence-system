from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core RAG settings
    chroma_persist_directory: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.1-8b-instant"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    # API Keys
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # Made optional to prevent crashes

    # Modern Pydantic V2 config: reads the .env file and safely ignores extra variables
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

settings = Settings()
