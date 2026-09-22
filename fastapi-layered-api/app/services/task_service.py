"""
Servicio de Tarea (capa de lógica de negocio).

Implementa las reglas de negocio y políticas de autorización a nivel
de objeto (BOLA):
- Garantiza que solo el propietario o un superusuario acceda o modifique sus tareas.
- Traduce las operaciones de dominio orquestando el TaskRepository.
- Lanza excepciones de dominio desacopladas de HTTP (TaskNotFoundError, TaskForbiddenError).
"""

from typing import Optional

from app.core.exceptions import TaskForbiddenError, TaskNotFoundError
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    async def create_task(self, *, owner_id: int, data: TaskCreate) -> Task:
        """Crea una nueva tarea asignada al usuario autenticado."""
        status_val = data.status.value if hasattr(data.status, "value") else str(data.status)
        priority_val = data.priority.value if hasattr(data.priority, "value") else str(data.priority)

        return await self._repository.create(
            owner_id=owner_id,
            title=data.title,
            description=data.description,
            status=status_val,
            priority=priority_val,
        )

    async def get_by_id(self, task_id: int, current_user: User) -> Task:
        """
        Obtiene una tarea por ID validando autorización a nivel de objeto (BOLA).
        Solo el dueño del recurso o un superusuario pueden consultar la tarea.
        """
        task = await self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Tarea con id={task_id} no encontrada.")

        if task.owner_id != current_user.id and not current_user.is_superuser:
            raise TaskForbiddenError("No tienes permisos para acceder a esta tarea.")

        return task

    async def list_tasks(
        self,
        current_user: User,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        """
        Lista tareas paginadas. Los usuarios comunes solo ven sus propias tareas;
        los superusuarios pueden consultar el listado global.
        """
        offset = (page - 1) * page_size
        owner_filter = None if current_user.is_superuser else current_user.id

        tasks, total = await self._repository.list(
            owner_id=owner_filter,
            status=status,
            offset=offset,
            limit=page_size,
        )
        return list(tasks), total

    async def update_task(self, task_id: int, data: TaskUpdate, current_user: User) -> Task:
        """Actualiza parcialmente una tarea previa validación de permisos."""
        task = await self.get_by_id(task_id, current_user)
        return await self._repository.update(task, data)

    async def delete_task(self, task_id: int, current_user: User) -> None:
        """Elimina una tarea previa validación de permisos."""
        task = await self.get_by_id(task_id, current_user)
        await self._repository.delete(task)
