from typing import Any


class WeightedReranker:
    weights = {
        "image_vector": 0.45,
        "caption_vector": 0.25,
        "metadata": 0.20,
        "caption_text": 0.10,
        "ocr_text": 0.10,
    }

    def rerank(
        self,
        items: list[dict[str, Any]],
        *,
        intent: dict[str, Any],
        plan: dict[str, Any],
    ) -> list[dict[str, Any]]:
        rerank_top_k = plan.get("rerank_top_k", 30)
        ranked = []
        for item in items:
            component_scores = item.get("component_scores", {})
            weighted = sum(
                self.weights.get(source, 0.05) * score
                for source, score in component_scores.items()
            )
            if not component_scores:
                weighted = item.get("score", 0.0)
            ranked.append(
                {
                    "image_id": item["image_id"],
                    "final_score": round(weighted, 6),
                    "component_scores": component_scores,
                    "evidence": item.get("payload", {}),
                }
            )
        ranked.sort(key=lambda item: item["final_score"], reverse=True)
        return ranked[:rerank_top_k]

