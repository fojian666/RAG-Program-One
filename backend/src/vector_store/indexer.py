from typing import Any


class VectorIndexer:
    def __init__(self, client: Any, collection_prefix: str = ""):
        self.client = client
        self.image_collection = f"{collection_prefix}image_embeddings" if collection_prefix else "image_embeddings"
        self.caption_collection = f"{collection_prefix}caption_embeddings" if collection_prefix else "caption_embeddings"

    async def upsert_image_vector(self, image_id: str, vector: list[float], payload: dict) -> None:
        await self._upsert(self.image_collection, image_id, vector, payload)

    async def upsert_caption_vector(
        self,
        image_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        await self._upsert(self.caption_collection, image_id, vector, payload)

    async def _upsert(
        self,
        collection: str,
        image_id: str,
        vector: list[float],
        payload: dict,
    ) -> None:
        await self.client.upsert(
            collection_name=collection,
            points=[{"id": image_id, "vector": vector, "payload": payload}],
        )
