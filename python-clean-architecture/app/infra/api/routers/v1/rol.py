from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.dtos.rol import CreateRolRequest, RolResponse, UpdateRol
from app.core.exceptions import (
    InvalidRolError,
    RolAlreadyExistsError,
    RolNotFoundError,
    UserNotFoundError,
)
from app.core.value_objects.id import InvalidIDError
from app.core.value_objects.role_name import InvalidRoleNameError
from app.infra.api.dependencies.usecases.rol import (
    CreateRol as CreateRolUsecase,
)
from app.infra.api.dependencies.usecases.rol import (
    DeleteRol as DeleteRolUsecase,
)
from app.infra.api.dependencies.usecases.rol import (
    GetRol as GetRolUsecase,
)
from app.infra.api.dependencies.usecases.rol import (
    UpdateRol as UpdateRolUsecase,
)

router = APIRouter()


@router.post(
    "",
    status_code=201,
    summary="Creates new Rol",
    responses={
        201: {"description": "Rol created successfully"},
        400: {"description": "Invalid rol data"},
        404: {"description": "User not found"},
        409: {"description": "Rol already exists or user already has a rol"},
    },
)
async def create(dto: CreateRolRequest, usecase: CreateRolUsecase) -> RolResponse:
    try:
        return await usecase.execute(dto)
    except (InvalidRolError, InvalidRoleNameError, InvalidIDError) as e:
        raise HTTPException(400, detail=str(e))
    except UserNotFoundError:
        raise HTTPException(404, detail="User not found")
    except RolAlreadyExistsError:
        raise HTTPException(409, detail="Rol already exists")


@router.get(
    "/user/{user_id}",
    summary="Gets Rol assigned to a user (1:1 relationship)",
    responses={
        200: {"description": "Rol found for user"},
        404: {"description": "Rol not found for user"},
    },
)
async def get_by_user(user_id: UUID, usecase: GetRolUsecase) -> RolResponse:
    try:
        return await usecase.execute_by_user_id(str(user_id))
    except InvalidIDError as e:
        raise HTTPException(status_code=422, detail=f"Invalid user ID: {e}")
    except RolNotFoundError:
        raise HTTPException(status_code=404, detail="Rol not found for user")


@router.get(
    "/{rol_id}",
    summary="Gets Rol information",
    responses={
        200: {"description": "Rol found"},
        404: {"description": "Rol not found"},
    },
)
async def get(rol_id: UUID, usecase: GetRolUsecase) -> RolResponse:
    try:
        return await usecase.execute(str(rol_id))
    except InvalidIDError as e:
        raise HTTPException(status_code=422, detail=f"Invalid rol ID: {e}")
    except RolNotFoundError:
        raise HTTPException(status_code=404, detail="Rol not found")


@router.delete(
    "/{rol_id}",
    status_code=204,
    summary="Deletes Rol",
    responses={
        204: {"description": "Rol deleted successfully"},
        404: {"description": "Rol not found"},
    },
)
async def delete(rol_id: UUID, usecase: DeleteRolUsecase) -> None:
    if not await usecase.execute(str(rol_id)):
        raise HTTPException(status_code=404, detail="Rol not found")


@router.patch(
    "/{rol_id}",
    summary="Updates Rol information",
    responses={
        200: {"description": "Rol updated"},
        400: {"description": "Invalid rol data"},
        404: {"description": "Rol not found"},
        409: {"description": "Rol name already taken"},
    },
)
async def patch(rol_id: UUID, dto: UpdateRol, usecase: UpdateRolUsecase) -> RolResponse:
    try:
        return await usecase.execute(str(rol_id), dto)
    except RolNotFoundError:
        raise HTTPException(status_code=404, detail="Rol not found")
    except RolAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Rol already exists")
    except (InvalidRolError, InvalidRoleNameError) as e:
        raise HTTPException(400, detail=str(e))
