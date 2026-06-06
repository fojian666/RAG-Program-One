from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import BatchTask, TaskLog
from src.models.enums import TaskStatus


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, *, task_type: str, user_instruction: str, plan: dict) -> BatchTask:
        task = BatchTask(task_type=task_type, user_instruction=user_instruction, plan=plan)
        self.session.add(task)
        await self.session.flush()
        return task

    async def mark_running(self, task: BatchTask) -> None:
        task.status = TaskStatus.RUNNING.value
        await self.session.flush()

    async def add_log(
        self,
        *,
        task_id: int,
        agent_name: str,
        action: str,
        status: str,
        message: str = "",
        image_id: str | None = None,
        payload: dict | None = None,
    ) -> TaskLog:
        log = TaskLog(
            task_id=task_id,
            image_id=image_id,
            agent_name=agent_name,
            action=action,
            status=status,
            message=message,
            payload=payload or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log

