class DuplicateTaskExecutor:
    async def execute(self, actions: list[dict]) -> list[dict]:
        return [{**action, "status": "planned"} for action in actions]

