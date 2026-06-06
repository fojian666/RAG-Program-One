from typing import Any

from src.graph.batch_graph import build_batch_graph


class BatchTaskService:
    def __init__(self, graph: Any | None = None):
        self.graph = graph or build_batch_graph()

    async def dry_run(self, instruction: str) -> dict[str, Any]:
        return await self.graph.ainvoke({"query": instruction})

