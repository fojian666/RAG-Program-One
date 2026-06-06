from collections import defaultdict
from typing import Any

from src.retrieval.caption_retriever import CaptionRetriever
from src.retrieval.metadata_retriever import MetadataRetriever
from src.retrieval.vector_retriever import VectorRetriever


class HybridRetriever:
    def __init__(
        self,
        *,
        vector_retriever: VectorRetriever | None = None,
        metadata_retriever: MetadataRetriever | None = None,
        caption_retriever: CaptionRetriever | None = None,
    ):
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.metadata_retriever = metadata_retriever or MetadataRetriever()
        self.caption_retriever = caption_retriever or CaptionRetriever()

    async def retrieve(
        self,
        *,
        query: str,
        intent: dict[str, Any],
        expanded_query: dict[str, Any],
        plan: dict[str, Any],
    ) -> list[dict[str, Any]]:
        top_k = plan.get("top_k", 100)
        filters = plan.get("metadata_filters", {})
        query_text = expanded_query.get("positive_text") or query

        candidates: list[dict[str, Any]] = []
        routes = set(plan.get("recall_routes", []))
        if "image_vector" in routes:
            candidates += await self.vector_retriever.search_image_vectors(
                query_text,
                top_k,
                filters,
            )
        if "caption_vector" in routes:
            candidates += await self.vector_retriever.search_caption_vectors(
                query_text,
                top_k,
                filters,
            )
        if "metadata" in routes:
            candidates += await self.metadata_retriever.search(filters, top_k)
        if "caption_text" in routes or "ocr_text" in routes:
            candidates += await self.caption_retriever.search(query_text, top_k)

        return self._merge(candidates)

    def _merge(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: dict[str, dict[str, Any]] = {}
        component_scores: dict[str, dict[str, float]] = defaultdict(dict)
        for candidate in candidates:
            image_id = candidate["image_id"]
            source = candidate.get("source", "unknown")
            score = float(candidate.get("score", 0.0))
            if image_id not in merged:
                merged[image_id] = {
                    "image_id": image_id,
                    "score": score,
                    "source": source,
                    "payload": candidate.get("payload", {}),
                }
            else:
                merged[image_id]["score"] = max(merged[image_id]["score"], score)
                merged[image_id]["payload"].update(candidate.get("payload", {}))
            component_scores[image_id][source] = max(
                component_scores[image_id].get(source, 0.0),
                score,
            )

        for image_id, item in merged.items():
            item["component_scores"] = component_scores[image_id]
        return sorted(merged.values(), key=lambda item: item["score"], reverse=True)
