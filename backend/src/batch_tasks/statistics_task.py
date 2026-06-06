class StatisticsTaskExecutor:
    async def execute(self, actions: list[dict]) -> dict:
        return {"total": len(actions)}

