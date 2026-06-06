from langgraph.graph import END, StateGraph

from src.agents.action_agent import ActionAgent
from src.agents.intent_agent import IntentAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.recall_agent import RecallAgent
from src.agents.report_agent import ReportAgent
from src.agents.rerank_agent import RerankAgent
from src.agents.vision_judge_agent import VisionJudgeAgent
from src.graph.state import BatchGraphState


def build_batch_graph():
    graph = StateGraph(BatchGraphState)

    graph.add_node("intent", IntentAgent().run)
    graph.add_node("planning", PlanningAgent().run)
    graph.add_node("recall", RecallAgent().run)
    graph.add_node("rerank", RerankAgent().run)
    graph.add_node("vision_judge", VisionJudgeAgent().run)
    graph.add_node("action", ActionAgent().run)
    graph.add_node("report", ReportAgent().run)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "planning")
    graph.add_edge("planning", "recall")
    graph.add_edge("recall", "rerank")
    graph.add_edge("rerank", "vision_judge")
    graph.add_edge("vision_judge", "action")
    graph.add_edge("action", "report")
    graph.add_edge("report", END)

    return graph.compile()

