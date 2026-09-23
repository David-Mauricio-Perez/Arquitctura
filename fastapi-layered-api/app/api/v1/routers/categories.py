"""
Router: Categorías (Recurso con endpoints públicos y mutaciones protegidas).

Aplica buenas prácticas de diseño RESTful:
- Endpoints de consulta abierta (GET /, GET /{id}) accesibles sin autenticación.
- Endpoints de mutación (POST, PATCH, DELETE) protegidos con OAuth2/JWT.
- Contratos tipados con Pydantic v2 (response_model explícito).
- Códigos de estado estándar (200 OK, 201 Created, 204 No Content, 404 Not Found, 409 Conflict).
- Paginación y control de volumen de respuesta para clientes públicos.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_category_service, get_current_active_user
from app.core.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryPublic,
    CategoryUpdate,
)
from app.schemas.common import ErrorResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


# ==============================================================================
# ENDPOINTS PÚBLICOS (Sin autenticación requerida)
# ==============================================================================


@router.get(
    "",
    response_model=CategoryListResponse,
    summary="Listar categorías disponibles (Acceso Público)",
    description="Permite a cualquier cliente consultar el catálogo de categorías sin autenticación.",
)
async def list_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
    page: Annotated[int, Query(ge=1, description="Número de página (1-indexado)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Tamaño de página (máx. 100)")
    ] = 20,
    only_active: Annotated[bool, Query(description="Filtrar solo categorías activas")] = True,
) -> CategoryListResponse:
    categories, total = await service.list_categories(
        page=page,
        page_size=page_size,
        only_active=only_active,
    )
    return CategoryListResponse(
        items=[CategoryPublic.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryPublic,
    summary="Obtener una categoría por ID (Acceso Público)",
    description="Consulta los detalles de una categoría específica sin necesidad de token.",
    responses={404: {"model": ErrorResponse, "description": "Categoría no encontrada"}},
)
async def get_category(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryPublic:
    try:
        category = await service.get_by_id(category_id)
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CategoryPublic.model_validate(category)


# ==============================================================================
# ENDPOINTS PROTEGIDOS (Requieren autenticación)
# ==============================================================================


@router.post(
    "",
    response_model=CategoryPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría (Protegido)",
    description="Requiere autenticación mediante token JWT.",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        409: {"model": ErrorResponse, "description": "Nombre de categoría ya en uso"},
    },
)
async def create_category(
    payload: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> CategoryPublic:
    try:
        category = await service.create_category(payload)
    except CategoryAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CategoryPublic.model_validate(category)


@router.patch(
    "/{category_id}",
    response_model=CategoryPublic,
    summary="Actualizar parcialmente una categoría (Protegido)",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Categoría no encontrada"},
        409: {"model": ErrorResponse, "description": "Nombre duplicado"},
    },
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> CategoryPublic:
    try:
        category = await service.update_category(category_id, payload)
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CategoryAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CategoryPublic.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría (Protegido)",
    responses={
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Categoría no encontrada"},
    },
)
async def delete_category(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> None:
    try:
        await service.delete_category(category_id)
    except CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
