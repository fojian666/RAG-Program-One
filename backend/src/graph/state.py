from typing import Any, TypedDict


class QueryGraphState(TypedDict, total=False):
    query: str
    intent: dict[str, Any]
    expanded_query: dict[str, Any]
    plan: dict[str, Any]
    filters: dict[str, Any]
    recalled_items: list[dict[str, Any]]
    reranked_items: list[dict[str, Any]]
    judged_items: list[dict[str, Any]]
    final_results: list[dict[str, Any]]
    explanations: list[dict[str, Any]]
    errors: list[str]


class BatchGraphState(QueryGraphState, total=False):
    actions: list[dict[str, Any]]
    report: dict[str, Any]

