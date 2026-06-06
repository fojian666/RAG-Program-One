from typing import Any

from src.agents.base import BaseAgent
from src.llm.client import LLMClient, get_llm_client
from src.models.schemas import ExpandedQuery, SemanticSlots
from src.prompts.loader import get_system_prompt


class QueryExpansionAgent(BaseAgent):
    name = "QueryExpansionAgent"

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or get_llm_client()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        intent = state.get("intent", {})
        query = intent.get("original_query") or state.get("query", "")
        slots = SemanticSlots(**intent.get("semantic_slots", {}))

        try:
            expanded = await self._llm_expand(query, slots)
        except Exception:
            expanded = self._fallback_expand(query, slots)

        return {"expanded_query": expanded.model_dump()}

    async def _llm_expand(self, query: str, slots: SemanticSlots) -> ExpandedQuery:
        system = get_system_prompt("query_expansion")
        output_schema = {
            "expanded_terms": ["string"],
            "semantic_slots": {
                "objects": ["string"],
                "scene": ["string"],
                "actions": ["string"],
                "emotion": ["string"],
                "context": ["string"],
                "visual_cues": ["string"],
                "ocr_keywords": ["string"],
            },
            "positive_text": "string",
            "negative_text": "string",
        }
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f'Query: "{query}"\n'
                    f"Semantic slots: {slots.model_dump()}\n\n"
                    f"Return JSON matching the schema."
                ),
            },
        ]
        result = await self.llm.chat_structured(messages, output_schema)
        merged_slots = slots.model_copy(
            update={
                "visual_cues": list(
                    set(slots.visual_cues + result.get("semantic_slots", {}).get("visual_cues", []))
                ),
                "ocr_keywords": list(
                    set(
                        slots.ocr_keywords
                        + result.get("semantic_slots", {}).get("ocr_keywords", [])
                    )
                ),
            }
        )
        return ExpandedQuery(
            original_query=query,
            expanded_terms=result.get("expanded_terms", []),
            semantic_slots=merged_slots,
            positive_text=result.get(
                "positive_text",
                " ".join([query, *result.get("expanded_terms", [])]).strip(),
            ),
            negative_text=result.get("negative_text", ""),
        )

    def _fallback_expand(self, query: str, slots: SemanticSlots) -> ExpandedQuery:
        expanded_terms = self._expand_terms(query, slots)
        expanded_slots = self._expand_slots(slots, expanded_terms)
        return ExpandedQuery(
            original_query=query,
            expanded_terms=expanded_terms,
            semantic_slots=expanded_slots,
            positive_text=" ".join([query, *expanded_terms]).strip(),
        )

    def _expand_terms(self, query: str, slots: SemanticSlots) -> list[str]:
        terms = set()
        if "home" in slots.scene or "家" in query:
            terms.update(["living room", "family", "cozy", "warm light", "indoor"])
        if "waiting" in slots.actions or "等待" in query:
            terms.update(["door", "window", "expectation", "looking out"])
        if "winter" in slots.context or "冬天" in query:
            terms.update(["snow", "cold", "coat", "festival", "indoor warmth"])
        if "lonely" in slots.emotion or "孤独" in query:
            terms.update(["single subject", "empty space", "quiet", "dim light"])
        if "cat" in slots.objects or "猫" in query:
            terms.update(["feline", "pet", "whiskers"])
        return sorted(terms)

    def _expand_slots(self, slots: SemanticSlots, terms: list[str]) -> SemanticSlots:
        visual_cues = list(slots.visual_cues)
        for term in terms:
            if term in {"warm light", "single subject", "empty space", "dim light", "looking out"}:
                visual_cues.append(term)
        return slots.model_copy(update={"visual_cues": sorted(set(visual_cues))})
