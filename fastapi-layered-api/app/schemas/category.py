"""
Schemas (contratos de la API) para el recurso Categoría (Category).

Sigue el patrón canónico de FastAPI (Base / Create / Update / Public):
- `CategoryBase`        -> campos comunes compartidos.
- `CategoryCreate`      -> datos requeridos para crear una categoría.
- `CategoryUpdate`      -> campos opcionales para una actualización parcial (PATCH).
- `CategoryPublic`      -> representación devuelta por la API (con id y fechas).
- `CategoryListResponse`-> respuesta con metadatos de paginación.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nombre único de la categoría.")
    description: Optional[str] = Field(None, max_length=255, description="Descripción opcional.")
    color: Optional[str] = Field("#6B7280", max_length=20, description="Código de color para la interfaz (ej. #3B82F6).")
    is_active: bool = Field(True, description="Estado de disponibilidad de la categoría.")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    """Campos opcionales para modificaciones parciales."""

    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nuevo nombre de la categoría.")
    description: Optional[str] = Field(None, max_length=255, description="Nueva descripción.")
    color: Optional[str] = Field(None, max_length=20, description="Nuevo color identificativo.")
    is_active: Optional[bool] = Field(None, description="Nuevo estado activo/inactivo.")


class CategoryPublic(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    """Envoltorio estándar con metadatos de paginación para consumo público."""

    items: list[CategoryPublic]
    total: int
    page: int
    page_size: int
