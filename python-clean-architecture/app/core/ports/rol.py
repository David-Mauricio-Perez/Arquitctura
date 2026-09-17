from typing import Protocol

from app.core.entities.rol import Rol
from app.core.ports.unit_of_work import UnitOfWork
from app.core.ports.user import UserRepo
from app.core.value_objects.id import ID
from app.core.value_objects.role_name import RoleName


class RolRepo(Protocol):
    """Protocol for rol repository operations."""

    async def save(self, rol: Rol) -> None:
        """Save a new rol.

        Args:
            rol: Rol entity to save
        """
        ...

    async def get_by_id(self, _id: ID) -> Rol | None:
        """Get a rol by ID.

        Args:
            _id: Rol ID

        Returns:
            Rol if found, None otherwise
        """
        ...

    async def get_by_name(self, name: RoleName) -> Rol | None:
        """Get a rol by name.

        Args:
            name: Rol name

        Returns:
            Rol if found, None otherwise
        """
        ...

    async def get_by_user_id(self, user_id: ID) -> Rol | None:
        """Get the rol assigned to a user (1:1 relationship).

        Args:
            user_id: User ID

        Returns:
            Rol if found, None otherwise
        """
        ...

    async def delete(self, _id: ID) -> bool:
        """Delete a rol by ID.

        Args:
            _id: Rol ID

        Returns:
            True if deleted, False if not found
        """
        ...

    async def update(self, rol: Rol) -> Rol | None:
        """Update an existing rol.

        Args:
            rol: Rol entity with updated data

        Returns:
            Updated rol if successful, None if not found
        """
        ...


class RolUnitOfWork(UnitOfWork, Protocol):
    """Unit of Work protocol for rol operations."""

    rol_repo: RolRepo
    user_repo: UserRepo
