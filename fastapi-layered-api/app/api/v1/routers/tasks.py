"""
Router: Tareas (recurso protegido).

Implementa las buenas prácticas de diseño de APIs RESTful:
- Uso semántico de verbos HTTP (POST para creación, GET para lectura, PATCH para
  actualización parcial y DELETE para borrado idempotente).
- Códigos de estado estándar (201 Created, 200 OK, 204 No Content, 403 Forbidden, 404 Not Found).
- Contratos de datos explícitos mediante schemas Pydantic v2 (response_model).
- Mitigación de OWASP API1:2023 (BOLA / IDOR): verificación de autorización para que
  cada usuario solo pueda consultar o alterar sus propias tareas.
- Paginación y filtrado seguro mediante query parameters.
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_active_user, get_task_service
from app.core.exceptions import TaskForbiddenError, TaskNotFoundError
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskPriority,
    TaskPublic,
    TaskStatus,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva tarea",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Usuario inactivo"},
    },
)
async def create_task(
    payload: TaskCreate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TaskPublic:
    task = await service.create_task(owner_id=current_user.id, data=payload)
    return TaskPublic.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="Listar tareas del usuario (paginado y filtrable)",
    responses={401: {"model": ErrorResponse, "description": "No autenticado"}},
)
async def list_tasks(
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_status: Annotated[
        Optional[TaskStatus], Query(alias="status", description="Filtrar por estado de la tarea")
    ] = None,
    page: Annotated[int, Query(ge=1, description="Número de página (1-indexado)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Tamaño de página (máx. 100)")
    ] = 20,
) -> TaskListResponse:
    status_value = task_status.value if task_status else None
    tasks, total = await service.list_tasks(
        current_user=current_user,
        status=status_value,
        page=page,
        page_size=page_size,
    )
    return TaskListResponse(
        items=[TaskPublic.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{task_id}",
    response_model=TaskPublic,
    summary="Obtener una tarea por ID",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Acceso denegado (BOLA)"},
        404: {"model": ErrorResponse, "description": "Tarea no encontrada"},
    },
)
async def get_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TaskPublic:
    try:
        task = await service.get_by_id(task_id, current_user)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TaskForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return TaskPublic.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskPublic,
    summary="Actualizar parcialmente una tarea",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Acceso denegado (BOLA)"},
        404: {"model": ErrorResponse, "description": "Tarea no encontrada"},
    },
)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TaskPublic:
    try:
        task = await service.update_task(task_id, payload, current_user)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TaskForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return TaskPublic.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una tarea",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Acceso denegado (BOLA)"},
        404: {"model": ErrorResponse, "description": "Tarea no encontrada"},
    },
)
async def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_task_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    try:
        await service.delete_task(task_id, current_user)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TaskForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
