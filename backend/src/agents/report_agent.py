from typing import Any

from src.agents.base import BaseAgent


class ReportAgent(BaseAgent):
    name = "ReportAgent"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        actions = state.get("actions", [])
        return {
            "report": {
                "total": len(actions),
                "dry_run": state.get("plan", {}).get("dry_run", True),
                "actions": actions,
            }
        }

