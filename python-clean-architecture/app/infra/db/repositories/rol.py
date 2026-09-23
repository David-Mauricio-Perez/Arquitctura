from uuid import uuid4

from sqlmodel import select

from app.core.entities.rol import Rol
from app.core.value_objects.id import ID
from app.core.value_objects.role_name import RoleName
from app.infra.db import DBSession
from app.infra.db.models.rol import Rol as DBRol


class RolRepo:
    def __init__(self, session: DBSession) -> None:
        self.session = session

    def new_id(self) -> str:
        """Generate a new UUID string for rol ID."""
        return str(uuid4())

    async def save(self, rol: Rol) -> None:
        """Save a new rol."""
        if rol.user_id is None:
            raise ValueError("Rol must be linked to a user")
        db_rol = DBRol(
            id=rol.id.value,
            name=rol.name.value,
            user_id=rol.user_id.value,
        )
        self.session.add(db_rol)

    async def get_by_id(self, _id: ID) -> Rol | None:
        """Get rol by ID."""
        db_rol = await self.session.get(DBRol, _id.value)
        if not db_rol:
            return None

        return self._to_entity(db_rol)

    async def get_by_name(self, name: RoleName) -> Rol | None:
        """Get rol by name."""
        result = await self.session.exec(select(DBRol).where(DBRol.name == name.value))
        db_rol = result.first()
        if not db_rol:
            return None

        return self._to_entity(db_rol)

    async def get_by_user_id(self, user_id: ID) -> Rol | None:
        """Get the rol assigned to a user (1:1)."""
        result = await self.session.exec(select(DBRol).where(DBRol.user_id == user_id.value))
        db_rol = result.first()
        if not db_rol:
            return None

        return self._to_entity(db_rol)

    async def delete(self, _id: ID) -> bool:
        """Delete rol by ID."""
        db_rol = await self.session.get(DBRol, _id.value)
        if not db_rol:
            return False
        await self.session.delete(db_rol)
        return True

    async def update(self, rol: Rol) -> Rol | None:
        """Update existing rol."""
        to_update = await self.session.get(DBRol, rol.id.value)
        if not to_update:
            return None

        to_update.name = rol.name.value
        self.session.add(to_update)
        return rol

    @staticmethod
    def _to_entity(db_rol: DBRol) -> Rol:
        """Map a DB model to a domain entity."""
        return Rol(
            id=ID.from_string(str(db_rol.id)),
            name=RoleName(db_rol.name),
            user_id=ID.from_string(str(db_rol.user_id)),
        )
