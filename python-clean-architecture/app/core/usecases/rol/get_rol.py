from dataclasses import dataclass

from app.core.dtos.rol import RolResponse
from app.core.exceptions import RolNotFoundError
from app.core.ports.rol import RolRepo
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class GetRolUsecase:
    rol_repo: RolRepo

    async def execute(self, rol_id: str) -> RolResponse:
        """Gets a rol by ID.

        Args:
            rol_id: The ID of the rol to get.

        Returns:
            RolResponse: The rol data.

        Raises:
            InvalidIDError: If the rol ID format is invalid.
            RolNotFoundError: If the rol is not found.
        """
        id_value = ID.from_string(rol_id)

        rol = await self.rol_repo.get_by_id(id_value)
        if not rol:
            raise RolNotFoundError(f"Rol with ID {rol_id} not found")

        return RolResponse(id=str(rol.id), name=rol.name.value, user_id=str(rol.user_id))

    async def execute_by_user_id(self, user_id: str) -> RolResponse:
        """Gets the rol assigned to a user (1:1 relationship).

        Args:
            user_id: The ID of the user.

        Returns:
            RolResponse: The rol data.

        Raises:
            InvalidIDError: If the user ID format is invalid.
            RolNotFoundError: If the user does not have an assigned rol.
        """
        id_value = ID.from_string(user_id)

        rol = await self.rol_repo.get_by_user_id(id_value)
        if not rol:
            raise RolNotFoundError(f"Rol for user ID {user_id} not found")

        return RolResponse(id=str(rol.id), name=rol.name.value, user_id=str(rol.user_id))

