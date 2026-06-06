from typing import Any


class RetrievalExplainer:
    def explain(
        self,
        items: list[dict[str, Any]],
        *,
        intent: dict[str, Any],
        expanded_query: dict[str, Any],
    ) -> list[dict[str, Any]]:
        results = []
        for item in items:
            reasons = self._build_reasons(item)
            explanation = {
                "image_id": item["image_id"],
                "score": item.get("final_score", 0.0),
                "reasons": reasons,
                "evidence": item.get("evidence", {}),
            }
            results.append(
                {
                    "image_id": item["image_id"],
                    "score": item.get("final_score", 0.0),
                    "explanation": explanation,
                }
            )
        return results

    def _build_reasons(self, item: dict[str, Any]) -> list[str]:
        evidence = item.get("evidence", {})
        metadata = evidence.get("metadata", {})
        caption = evidence.get("caption")
        reasons = []
        for key in ["objects", "scene", "actions", "emotion", "context"]:
            values = metadata.get(key) or []
            if values:
                reasons.append(f"{key} matched: {', '.join(values)}")
        if caption:
            reasons.append("caption provides semantic support")
        if not reasons:
            reasons.append("matched by hybrid retrieval score")
        return reasons

