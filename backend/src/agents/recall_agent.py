from typing import Any

from src.agents.base import BaseAgent
from src.retrieval.hybrid_retriever import HybridRetriever


class RecallAgent(BaseAgent):
    name = "RecallAgent"

    def __init__(self, retriever: HybridRetriever | None = None):
        self.retriever = retriever or HybridRetriever()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        items = await self.retriever.retrieve(
            query=state.get("query", ""),
            intent=state.get("intent", {}),
            expanded_query=state.get("expanded_query", {}),
            plan=state.get("plan", {}),
        )
        return {"recalled_items": items}

