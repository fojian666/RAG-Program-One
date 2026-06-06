import pytest

from src.agents.intent_agent import IntentAgent
from src.agents.query_expansion_agent import QueryExpansionAgent


@pytest.mark.asyncio
async def test_intent_agent_extracts_implicit_home_query():
    state = await IntentAgent().run({"query": "找出有家的感觉的照片"})

    slots = state["intent"]["semantic_slots"]
    assert state["intent"]["intent_type"] == "semantic_search"
    assert "home" in slots["scene"]


@pytest.mark.asyncio
async def test_query_expansion_adds_visual_cues():
    intent_state = await IntentAgent().run({"query": "等待主人的宠物"})
    expanded = await QueryExpansionAgent().run({"query": "等待主人的宠物", **intent_state})

    assert "looking out" in expanded["expanded_query"]["expanded_terms"]
    assert "expectation" in expanded["expanded_query"]["expanded_terms"]

