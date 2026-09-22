"""
Schemas (contratos de la API) para el recurso Tarea (Task).

Sigue el patrón canónico de FastAPI (Base / Create / Update / Public):
- `TaskBase`        -> campos comunes compartidos.
- `TaskCreate`      -> datos requeridos para crear una tarea.
- `TaskUpdate`      -> campos opcionales para una actualización parcial (PATCH/PUT).
- `TaskPublic`      -> representación que la API devuelve (incluye id, owner_id y fechas).
- `TaskListResponse`-> respuesta con metadatos de paginación.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Título descriptivo de la tarea.")
    description: Optional[str] = Field(None, max_length=1000, description="Detalle opcional de la tarea.")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Estado actual de la tarea.")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Nivel de prioridad.")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """Todos los campos son opcionales para permitir actualizaciones parciales (PATCH)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Nuevo título de la tarea.")
    description: Optional[str] = Field(None, max_length=1000, description="Nueva descripción de la tarea.")
    status: Optional[TaskStatus] = Field(None, description="Nuevo estado de la tarea.")
    priority: Optional[TaskPriority] = Field(None, description="Nueva prioridad de la tarea.")


class TaskPublic(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Envoltorio estándar con metadatos de paginación."""

    items: list[TaskPublic]
    total: int
    page: int
    page_size: int
