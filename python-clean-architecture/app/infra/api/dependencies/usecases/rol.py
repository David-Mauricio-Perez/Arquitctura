from typing import Annotated

from fastapi import Depends

from app.core.usecases.rol import (
    CreateRolUsecase,
    DeleteRolUsecase,
    GetRolUsecase,
    UpdateRolUsecase,
)
from app.infra.api.dependencies.rol import Repo, UnitOfWork


def get_create_rol_usecase(uow: UnitOfWork) -> CreateRolUsecase:
    return CreateRolUsecase(uow)


def get_get_rol_usecase(repo: Repo) -> GetRolUsecase:
    return GetRolUsecase(repo)


def get_update_rol_usecase(uow: UnitOfWork) -> UpdateRolUsecase:
    return UpdateRolUsecase(uow)


def get_delete_rol_usecase(uow: UnitOfWork) -> DeleteRolUsecase:
    return DeleteRolUsecase(uow)


CreateRol = Annotated[CreateRolUsecase, Depends(get_create_rol_usecase)]
GetRol = Annotated[GetRolUsecase, Depends(get_get_rol_usecase)]
UpdateRol = Annotated[UpdateRolUsecase, Depends(get_update_rol_usecase)]
DeleteRol = Annotated[DeleteRolUsecase, Depends(get_delete_rol_usecase)]
