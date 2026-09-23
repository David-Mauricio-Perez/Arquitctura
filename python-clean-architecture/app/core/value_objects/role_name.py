from dataclasses import dataclass


class InvalidRoleNameError(Exception):
    pass


@dataclass(frozen=True)
class RoleName:
    """Value object representing a validated role name (snake_case identifier)."""

    value: str
    _ROLE_NAME_PATTERN = r"^[a-z][a-z0-9_]{1,49}$"

    def __post_init__(self):
        import re

        if not re.match(self._ROLE_NAME_PATTERN, self.value):
            raise InvalidRoleNameError(
                f"Role name must be 2-50 chars, lowercase letters, digits or underscore: {self.value}"
            )
