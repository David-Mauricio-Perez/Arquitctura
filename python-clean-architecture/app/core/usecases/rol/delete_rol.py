from dataclasses import dataclass

from app.core.ports.rol import RolUnitOfWork
from app.core.value_objects.id import ID
from app.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(frozen=True)
class DeleteRolUsecase:
    uow: RolUnitOfWork

    async def execute(self, rol_id: str) -> bool:
        """Deletes a rol.

        Args:
            rol_id: The ID of the rol to delete.

        Returns:
            True if the rol was deleted, False otherwise.

        Raises:
            InvalidIDError: If the rol ID format is invalid.
        """
        id_value = ID.from_string(rol_id)

        async with self.uow:
            result = await self.uow.rol_repo.delete(id_value)
            if result:
                logger.info(f"Rol {rol_id} deleted successfully")
            return result
