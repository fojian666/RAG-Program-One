from functools import lru_cache

import httpx

from src.config.settings import Settings, get_settings
from src.embeddings.base import TextEmbedder


class BailianTextEmbedder:
    """Text embedder using Aliyun Bailian OpenAI-compatible embedding API."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.api_key = self.settings.embedding_api_key or self.settings.llm_api_key
        self.base_url = (self.settings.embedding_base_url or self.settings.llm_base_url).rstrip("/")
        self.model = self.settings.embedding_model
        self.dimensions = self.settings.embedding_dimensions

    async def embed_text(self, text: str) -> list[float]:
        if not self.api_key:
            raise ValueError("EMBEDDING_API_KEY or LLM_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
            "dimensions": self.dimensions,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]


# Compatibility alias
TextEmbedderAdapter = BailianTextEmbedder


@lru_cache
def get_text_embedder() -> TextEmbedder:
    return BailianTextEmbedder()
