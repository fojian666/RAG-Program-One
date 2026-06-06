from typing import Any

from src.agents.base import BaseAgent


class ActionAgent(BaseAgent):
    name = "ActionAgent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        plan = state.get("plan", {})
        items = state.get("judged_items", [])
        actions = [
            {
                "image_id": item["image_id"],
                "action": state.get("intent", {}).get("task_type", "noop"),
                "dry_run": plan.get("dry_run", True),
                "reason": "candidate passed retrieval and saved-metadata verification",
            }
            for item in items
        ]
        return {"actions": actions}

