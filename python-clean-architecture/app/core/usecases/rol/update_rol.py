from dataclasses import dataclass

from app.core.dtos.rol import RolResponse, UpdateRol
from app.core.entities.rol import Rol
from app.core.exceptions import InvalidRolError, RolAlreadyExistsError, RolNotFoundError
from app.core.ports.rol import RolUnitOfWork
from app.core.value_objects.id import ID
from app.core.value_objects.role_name import InvalidRoleNameError, RoleName
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class UpdateRolUsecase:
    uow: RolUnitOfWork

    async def execute(self, rol_id: str, dto: UpdateRol) -> RolResponse:
        """Updates a rol name.

        Args:
            rol_id: The ID of the rol to update.
            dto: The data to update the rol with.

        Returns:
            RolResponse: The updated rol data.

        Raises:
            InvalidIDError: If the rol ID format is invalid.
            InvalidRolError: If the rol name format is invalid.
            RolNotFoundError: If the rol is not found.
            RolAlreadyExistsError: If the new name is already taken.
        """
        id_value = ID.from_string(rol_id)

        try:
            name = RoleName(dto.name) if dto.name else None
        except InvalidRoleNameError as e:
            logger.warning(f"Invalid rol name: {e}")
            raise InvalidRolError(str(e))

        async with self.uow:
            existing_rol = await self.uow.rol_repo.get_by_id(id_value)
            if not existing_rol:
                raise RolNotFoundError(f"Rol with ID {rol_id} not found")

            if name:
                rol_with_name = await self.uow.rol_repo.get_by_name(name)
                if rol_with_name and rol_with_name.id != existing_rol.id:
                    raise RolAlreadyExistsError(f"Rol with name {name.value} already exists")

            updated_rol = await self.uow.rol_repo.update(
                Rol(
                    id=existing_rol.id,
                    name=name or existing_rol.name,
                    user_id=existing_rol.user_id,
                )
            )

            if not updated_rol:
                raise RolNotFoundError(f"Rol with ID {rol_id} not found")

            logger.info(f"Rol {rol_id} updated successfully")
            return RolResponse(
                id=str(updated_rol.id),
                name=updated_rol.name.value,
                user_id=str(updated_rol.user_id),
            )
