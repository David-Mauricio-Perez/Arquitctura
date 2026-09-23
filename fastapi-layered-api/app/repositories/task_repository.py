"""
Repositorio de Tarea (patrón Repository).

Responsabilidad única: traducir operaciones de persistencia de tareas
a consultas SQLAlchemy. Desacoplado de FastAPI y de las reglas de negocio.
"""

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        return await self._session.get(Task, task_id)

    async def list(
        self,
        *,
        owner_id: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Task], int]:
        query = select(Task)
        count_query = select(func.count()).select_from(Task)

        if owner_id is not None:
            query = query.where(Task.owner_id == owner_id)
            count_query = count_query.where(Task.owner_id == owner_id)

        if status is not None:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)

        query = query.order_by(Task.id.desc()).offset(offset).limit(limit)

        items_result = await self._session.execute(query)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        return items_result.scalars().all(), total

    async def create(
        self,
        *,
        owner_id: int,
        title: str,
        description: Optional[str],
        status: str,
        priority: str,
        category_id: Optional[int] = None,
    ) -> Task:
        task = Task(
            owner_id=owner_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            category_id=category_id,
        )
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def update(self, task: Task, data: TaskUpdate) -> Task:
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.status is not None:
            task.status = data.status.value if hasattr(data.status, "value") else data.status
        if data.priority is not None:
            task.priority = data.priority.value if hasattr(data.priority, "value") else data.priority
        if data.category_id is not None:
            task.category_id = data.category_id

        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self._session.delete(task)
        await self._session.flush()
