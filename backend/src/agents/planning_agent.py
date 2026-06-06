from typing import Any

from src.agents.base import BaseAgent
from src.models.enums import RetrievalRoute
from src.models.schemas import RetrievalPlan


class PlanningAgent(BaseAgent):
    name = "PlanningAgent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        intent = state.get("intent", {})
        slots = intent.get("semantic_slots", {})
        routes = [
            RetrievalRoute.IMAGE_VECTOR.value,
            RetrievalRoute.CAPTION_VECTOR.value,
            RetrievalRoute.METADATA.value,
            RetrievalRoute.CAPTION_TEXT.value,
        ]
        if slots.get("ocr_keywords"):
            routes.append(RetrievalRoute.OCR_TEXT.value)

        plan = RetrievalPlan(
            strategy="hybrid",
            recall_routes=routes,
            metadata_filters=self._metadata_filters(slots),
            dry_run=True,
        )
        return {"plan": plan.model_dump(), "filters": plan.metadata_filters}

    def _metadata_filters(self, slots: dict[str, Any]) -> dict[str, Any]:
        filters = {}
        for key in ["objects", "scene", "actions", "emotion", "context"]:
            values = slots.get(key) or []
            if values:
                filters[key] = values
        return filters

