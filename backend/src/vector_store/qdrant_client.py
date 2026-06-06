from qdrant_client import AsyncQdrantClient

from src.config.settings import get_settings


def build_qdrant_client() -> AsyncQdrantClient:
    settings = get_settings()
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

