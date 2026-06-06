from typing import Any

from src.agents.base import BaseAgent
from src.llm.client import LLMClient, get_llm_client
from src.models.enums import BatchTaskType, IntentType
from src.models.schemas import QueryIntent, SemanticSlots
from src.prompts.loader import get_system_prompt


class IntentAgent(BaseAgent):
    name = "IntentAgent"

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or get_llm_client()

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        query = state.get("query", "").strip()
        if not query:
            return {
                "intent": QueryIntent(
                    original_query="", intent_type=IntentType.SEMANTIC_SEARCH.value
                ).model_dump()
            }

        try:
            intent = await self._llm_intent(query)
        except Exception:
            intent = self._fallback_intent(query)

        return {"intent": intent.model_dump()}

    async def _llm_intent(self, query: str) -> QueryIntent:
        system = get_system_prompt("intent")
        output_schema = {
            "intent_type": "semantic_search | batch_action | ocr_search | statistics",
            "task_type": (
                "archive | tagging | deduplicate | ocr_filter | blur_filter | statistics | null"
            ),
            "semantic_slots": {
                "objects": ["string"],
                "scene": ["string"],
                "actions": ["string"],
                "emotion": ["string"],
                "context": ["string"],
                "visual_cues": ["string"],
                "ocr_keywords": ["string"],
            },
        }
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f'Query: "{query}"\n\nReturn JSON matching the schema.'},
        ]
        result = await self.llm.chat_structured(messages, output_schema)
        return QueryIntent(
            original_query=query,
            intent_type=result.get("intent_type", IntentType.SEMANTIC_SEARCH.value),
            task_type=result.get("task_type"),
            semantic_slots=SemanticSlots(**result.get("semantic_slots", {})),
        )

    def _fallback_intent(self, query: str) -> QueryIntent:
        task_type = self._detect_task_type(query)
        intent_type = (
            IntentType.BATCH_ACTION.value
            if task_type
            else IntentType.SEMANTIC_SEARCH.value
        )
        slots = self._extract_slots(query)
        return QueryIntent(
            original_query=query,
            intent_type=intent_type,
            task_type=task_type,
            semantic_slots=slots,
        )

    def _detect_task_type(self, query: str) -> str | None:
        if any(word in query for word in ["归档", "整理", "移动到"]):
            return BatchTaskType.ARCHIVE.value
        if any(word in query for word in ["打标签", "标记"]):
            return BatchTaskType.TAGGING.value
        if any(word in query for word in ["重复", "相似"]):
            return BatchTaskType.DEDUPLICATE.value
        if any(word in query for word in ["统计", "分析数量"]):
            return BatchTaskType.STATISTICS.value
        return None

    def _extract_slots(self, query: str) -> SemanticSlots:
        objects: list[str] = []
        scene: list[str] = []
        actions: list[str] = []
        emotion: list[str] = []
        context: list[str] = []

        keyword_map = {
            "猫": ("objects", "cat"),
            "狗": ("objects", "dog"),
            "宠物": ("objects", "pet"),
            "人": ("objects", "person"),
            "家": ("scene", "home"),
            "客厅": ("scene", "living room"),
            "冬天": ("context", "winter"),
            "雪": ("context", "snow"),
            "等待": ("actions", "waiting"),
            "温馨": ("emotion", "warm"),
            "家庭": ("emotion", "family"),
            "孤独": ("emotion", "lonely"),
        }

        buckets = {
            "objects": objects,
            "scene": scene,
            "actions": actions,
            "emotion": emotion,
            "context": context,
        }
        for keyword, (bucket, value) in keyword_map.items():
            if keyword in query:
                buckets[bucket].append(value)

        return SemanticSlots(
            objects=objects,
            scene=scene,
            actions=actions,
            emotion=emotion,
            context=context,
        )
