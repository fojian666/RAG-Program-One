from typing import Any

from pydantic import BaseModel, Field


class SemanticSlots(BaseModel):
    objects: list[str] = Field(default_factory=list)
    scene: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    emotion: list[str] = Field(default_factory=list)
    context: list[str] = Field(default_factory=list)
    visual_cues: list[str] = Field(default_factory=list)
    ocr_keywords: list[str] = Field(default_factory=list)


class QueryIntent(BaseModel):
    original_query: str
    intent_type: str
    task_type: str | None = None
    semantic_slots: SemanticSlots = Field(default_factory=SemanticSlots)
    filters: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)


class ExpandedQuery(BaseModel):
    original_query: str
    expanded_terms: list[str] = Field(default_factory=list)
    semantic_slots: SemanticSlots = Field(default_factory=SemanticSlots)
    positive_text: str = ""
    negative_text: str = ""


class RetrievalPlan(BaseModel):
    strategy: str = "hybrid"
    recall_routes: list[str] = Field(default_factory=list)
    metadata_filters: dict[str, Any] = Field(default_factory=dict)
    top_k: int = 100
    rerank_top_k: int = 30
    dry_run: bool = True


class RetrievedItem(BaseModel):
    image_id: str
    score: float
    source: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RankedItem(BaseModel):
    image_id: str
    final_score: float
    component_scores: dict[str, float] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)


class ExplainedResult(BaseModel):
    image_id: str
    score: float
    reasons: list[str]
    evidence: dict[str, Any] = Field(default_factory=dict)

