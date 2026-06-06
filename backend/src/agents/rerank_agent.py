from typing import Any

from src.agents.base import BaseAgent
from src.retrieval.reranker import WeightedReranker


class RerankAgent(BaseAgent):
    name = "RerankAgent"

    def __init__(self, reranker: WeightedReranker | None = None):
        self.reranker = reranker or WeightedReranker()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        ranked = self.reranker.rerank(
            state.get("recalled_items", []),
            intent=state.get("intent", {}),
            plan=state.get("plan", {}),
        )
        return {"reranked_items": ranked}

