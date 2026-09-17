from dataclasses import dataclass

from app.core.exceptions import InvalidRolError
from app.core.value_objects.id import ID
from app.core.value_objects.role_name import RoleName


@dataclass(frozen=True, kw_only=True)
class Rol:
    id: ID
    name: RoleName
    user_id: ID

    def __post_init__(self):
        if self.user_id is None:
            raise InvalidRolError("Rol must be linked to a user (user_id is required)")
