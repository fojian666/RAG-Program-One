from src.embeddings.text_embedder import BailianTextEmbedder
from src.vector_store.local_client import LocalVectorClient


class LocalVectorSearchBackend:
    """Local-file-backed vector search with Bailian text embeddings."""

    def __init__(self, embedder: BailianTextEmbedder | None = None):
        self.client = LocalVectorClient()
        self.embedder = embedder or BailianTextEmbedder()

    async def search(
        self,
        collection: str,
        query_text: str,
        top_k: int,
        filters: dict,
    ) -> list[dict]:
        vector = await self.embedder.embed_text(query_text)
        query_filter = self._build_filter(filters) if filters else None

        results = await self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        return [
            {
                "image_id": str(point["id"]),
                "score": point["score"],
                "source": collection.replace("_embeddings", "_vector"),
                "payload": point.get("payload", {}),
            }
            for point in results
        ]

    def _build_filter(self, filters: dict) -> dict | None:
        # Simple payload filter: match any of the values per key
        if not filters:
            return None
        must_conditions = []
        for key, values in filters.items():
            if isinstance(values, list) and values:
                must_conditions.append(
                    {
                        "key": f"metadata.{key}",
                        "match": {"any": values},
                    }
                )
        return {"must": must_conditions} if must_conditions else None
