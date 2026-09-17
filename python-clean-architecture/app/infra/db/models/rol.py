from uuid import UUID

from sqlmodel import Field, SQLModel


class Rol(SQLModel, table=True):
    __tablename__ = "roles"

    id: UUID = Field(primary_key=True)
    name: str = Field(unique=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True)
