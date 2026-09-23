from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from app.core.ports import rol
from app.infra.db import async_session
from app.infra.db.repositories.rol import RolRepo
from app.infra.db.unit_of_work.rol import rol_uow_factory


async def get_rol_repo() -> AsyncGenerator[rol.RolRepo, None]:
    async with async_session() as session:
        yield RolRepo(session)


async def get_rol_uow() -> AsyncGenerator[rol.RolUnitOfWork, None]:
    async with async_session() as session:
        yield rol_uow_factory(session)  # type: ignore[misc]


Repo = Annotated[rol.RolRepo, Depends(get_rol_repo)]
UnitOfWork = Annotated[rol.RolUnitOfWork, Depends(get_rol_uow)]
