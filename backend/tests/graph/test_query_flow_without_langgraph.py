import pytest

from src.agents.intent_agent import IntentAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.query_expansion_agent import QueryExpansionAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.rerank_agent import RerankAgent
from src.agents.vision_judge_agent import VisionJudgeAgent


@pytest.mark.asyncio
async def test_query_agent_flow_with_injected_candidates():
    state = {"query": "找出所有猫的图片"}
    state.update(await IntentAgent().run(state))
    state.update(await QueryExpansionAgent().run(state))
    state.update(await PlanningAgent().run(state))
    state["recalled_items"] = [
        {
            "image_id": "img-1",
            "score": 0.9,
            "component_scores": {"metadata": 0.9},
            "payload": {"metadata": {"objects": ["cat"]}, "caption": "cat at home"},
        }
    ]
    state.update(await RerankAgent().run(state))
    state.update(await VisionJudgeAgent().run(state))
    state.update(await ReasoningAgent().run(state))

    assert state["final_results"][0]["image_id"] == "img-1"
    assert state["explanations"][0]["reasons"]

