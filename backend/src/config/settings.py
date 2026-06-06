from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_PROJECT_ROOT / ".env"), extra="ignore")

    app_name: str = "agentic-image-rag"
    environment: str = "local"

    # Backend switches: local | postgresql / local | qdrant / local | minio
    db_backend: str = "sqlite"
    database_url: str = f"sqlite+aiosqlite:///{_PROJECT_ROOT / 'data' / 'agentic_image_rag.db'}"

    vector_backend: str = "local"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    storage_backend: str = "local"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "images"

    # Local paths (used when backend == local)
    local_storage_path: str = str(_PROJECT_ROOT / "data" / "images")
    local_vector_path: str = str(_PROJECT_ROOT / "data" / "vectors")

    # Aliyun Bailian (OpenAI-compatible)
    # Default endpoint: https://dashscope.aliyuncs.com/compatible-mode/v1
    llm_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-turbo"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 2048
    llm_timeout: int = 60

    # Vision Model (Bailian Qwen-VL)
    vision_api_key: str = ""
    vision_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    vision_model: str = "qwen-vl-max"

    # Text Embeddings (Bailian)
    embedding_api_key: str = ""
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "text-embedding-v3"
    embedding_dimensions: int = 1024

    # Image embedder: local SigLIP model path (recommended for 10k+ images)
    # If empty, image vector search will be skipped
    siglip_model_path: str = ""

    # Concurrency limits for large-scale ingestion
    ingestion_concurrency: int = 8
    ingestion_max_retries: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
