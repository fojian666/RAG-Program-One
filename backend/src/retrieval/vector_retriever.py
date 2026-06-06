from typing import Protocol

from src.config.settings import get_settings
from src.vector_store.backend import QdrantVectorSearchBackend
from src.vector_store.local_backend import LocalVectorSearchBackend


class VectorSearchBackend(Protocol):
    async def search(
        self,
        collection: str,
        query_text: str,
        top_k: int,
        filters: dict,
    ) -> list[dict]:
        ...


def _get_default_backend() -> VectorSearchBackend:
    settings = get_settings()
    if settings.vector_backend == "local":
        return LocalVectorSearchBackend()
    return QdrantVectorSearchBackend()


class VectorRetriever:
    def __init__(self, backend: VectorSearchBackend | None = None):
        self.backend = backend or _get_default_backend()

    async def search_image_vectors(self, query_text: str, top_k: int, filters: dict) -> list[dict]:
        return await self.backend.search("image_embeddings", query_text, top_k, filters)

    async def search_caption_vectors(
        self,
        query_text: str,
        top_k: int,
        filters: dict,
    ) -> list[dict]:
        return await self.backend.search("caption_embeddings", query_text, top_k, filters)
