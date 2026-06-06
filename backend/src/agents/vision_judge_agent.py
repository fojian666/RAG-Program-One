from typing import Any

from src.agents.base import BaseAgent


class VisionJudgeAgent(BaseAgent):
    name = "VisionJudgeAgent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        filters = state.get("filters", {})
        judged = []
        for item in state.get("reranked_items", []):
            evidence = item.get("evidence", {})
            matched = self._matches_metadata_filters(evidence, filters)
            if matched:
                judged.append({**item, "judge_passed": True})
        return {"judged_items": judged}

    def _matches_metadata_filters(self, evidence: dict[str, Any], filters: dict[str, Any]) -> bool:
        if not filters:
            return True
        metadata = evidence.get("metadata", {})
        for key, expected in filters.items():
            actual = set(metadata.get(key, []))
            if expected and not actual.intersection(expected):
                return False
        return True

