from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CreateRolRequest:
    name: str
    user_id: str


@dataclass(frozen=True, kw_only=True)
class RolResponse:
    id: str
    name: str
    user_id: str


@dataclass(frozen=True)
class UpdateRol:
    name: str | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("At least one field must be provided")
