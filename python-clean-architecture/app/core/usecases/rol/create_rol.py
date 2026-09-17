from dataclasses import dataclass

from app.core.dtos.rol import CreateRolRequest, RolResponse
from app.core.entities.rol import Rol
from app.core.exceptions import (
    InvalidRolError,
    RolAlreadyExistsError,
    UserNotFoundError,
)
from app.core.ports.rol import RolUnitOfWork
from app.core.value_objects.id import ID, InvalidIDError
from app.core.value_objects.role_name import InvalidRoleNameError, RoleName
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class CreateRolUsecase:
    uow: RolUnitOfWork

    async def execute(self, dto: CreateRolRequest) -> RolResponse:
        """Creates a new rol assigned to a user (1:1 relationship).

        Args:
            dto (CreateRolRequest): The data to create the rol with.

        Returns:
            RolResponse: The created rol.

        Raises:
            InvalidRolError: If the input data to create the rol is invalid.
            UserNotFoundError: If the target user does not exist.
            RolAlreadyExistsError: If the rol name or the user already has a rol.
        """
        try:
            name = RoleName(dto.name)
            user_id = ID.from_string(dto.user_id)
        except (InvalidRoleNameError, InvalidIDError) as e:
            logger.warning(f"Invalid rol: {e}")
            raise InvalidRolError(str(e))

        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {dto.user_id} not found")

            if await self.uow.rol_repo.get_by_name(name):
                logger.warning(f"Rol with name {name.value} already exists")
                raise RolAlreadyExistsError(f"Rol with name {name.value} already exists")

            if await self.uow.rol_repo.get_by_user_id(user_id):
                logger.warning(f"User {dto.user_id} already has a rol (1:1 relationship)")
                raise RolAlreadyExistsError(f"User with ID {dto.user_id} already has a rol")

            rol = Rol(id=ID.generate(), name=name, user_id=user_id)

            await self.uow.rol_repo.save(rol)
            logger.info(f"Rol {rol.name.value} created and assigned to user {dto.user_id}")
            return RolResponse(id=str(rol.id), name=rol.name.value, user_id=str(rol.user_id))
