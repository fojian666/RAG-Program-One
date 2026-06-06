from langgraph.graph import END, StateGraph

from src.agents.intent_agent import IntentAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.query_expansion_agent import QueryExpansionAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.recall_agent import RecallAgent
from src.agents.rerank_agent import RerankAgent
from src.agents.vision_judge_agent import VisionJudgeAgent
from src.graph.state import QueryGraphState


def build_query_graph():
    graph = StateGraph(QueryGraphState)

    graph.add_node("intent", IntentAgent().run)
    graph.add_node("query_expansion", QueryExpansionAgent().run)
    graph.add_node("planning", PlanningAgent().run)
    graph.add_node("recall", RecallAgent().run)
    graph.add_node("rerank", RerankAgent().run)
    graph.add_node("vision_judge", VisionJudgeAgent().run)
    graph.add_node("reasoning", ReasoningAgent().run)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "query_expansion")
    graph.add_edge("query_expansion", "planning")
    graph.add_edge("planning", "recall")
    graph.add_edge("recall", "rerank")
    graph.add_edge("rerank", "vision_judge")
    graph.add_edge("vision_judge", "reasoning")
    graph.add_edge("reasoning", END)

    return graph.compile()

