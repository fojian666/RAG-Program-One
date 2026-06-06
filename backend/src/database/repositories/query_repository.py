from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import QueryHistory, QueryResult


class QueryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_query(
        self,
        *,
        query_text: str,
        intent: dict,
        expanded_query: dict,
        plan: dict,
        filters: dict,
        results: list[dict],
        latency_ms: int | None = None,
    ) -> QueryHistory:
        query = QueryHistory(
            query_text=query_text,
            intent=intent,
            expanded_query=expanded_query,
            plan=plan,
            filters=filters,
            result_count=len(results),
            latency_ms=latency_ms,
        )
        self.session.add(query)
        await self.session.flush()

        for rank, result in enumerate(results, start=1):
            self.session.add(
                QueryResult(
                    query_id=query.id,
                    image_id=result["image_id"],
                    score=result.get("score", 0.0),
                    rank=rank,
                    explanation=result.get("explanation", {}),
                )
            )
        return query

