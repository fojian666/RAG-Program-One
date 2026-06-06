from typing import Any

from src.agents.base import BaseAgent
from src.llm.client import LLMClient, get_llm_client
from src.prompts.loader import get_system_prompt
from src.retrieval.explain import RetrievalExplainer


class ReasoningAgent(BaseAgent):
    name = "ReasoningAgent"

    def __init__(
        self,
        explainer: RetrievalExplainer | None = None,
        llm: LLMClient | None = None,
    ):
        self.explainer = explainer or RetrievalExplainer()
        self.llm = llm or get_llm_client()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        judged_items = state.get("judged_items", [])
        intent = state.get("intent", {})
        expanded_query = state.get("expanded_query", {})

        try:
            results = await self._llm_explain(judged_items, intent, expanded_query)
        except Exception:
            results = self.explainer.explain(
                judged_items, intent=intent, expanded_query=expanded_query
            )

        return {
            "final_results": results,
            "explanations": [item.get("explanation", {}) for item in results],
        }

    async def _llm_explain(
        self,
        items: list[dict[str, Any]],
        intent: dict[str, Any],
        expanded_query: dict[str, Any],
    ) -> list[dict[str, Any]]:
        system = get_system_prompt("reasoning")
        output_schema = {
            "explanations": [
                {
                    "image_id": "string",
                    "score": "number",
                    "reasons": ["string"],
                    "evidence": {},
                }
            ]
        }
        context = {
            "user_query": intent.get("original_query", ""),
            "expanded_terms": expanded_query.get("expanded_terms", []),
            "items": [
                {
                    "image_id": item.get("image_id"),
                    "score": item.get("final_score", 0.0),
                    "evidence": item.get("evidence", {}),
                }
                for item in items
            ],
        }
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"Context: {context}\n\n"
                    f"Return JSON matching the schema with explanations for each image."
                ),
            },
        ]
        result = await self.llm.chat_structured(messages, output_schema)
        explanations = result.get("explanations", [])
        # Map back to the expected structure
        mapped = []
        for item, expl in zip(items, explanations, strict=False):
            mapped.append(
                {
                    "image_id": expl.get("image_id", item.get("image_id")),
                    "score": expl.get("score", item.get("final_score", 0.0)),
                    "explanation": expl,
                }
            )
        return mapped
