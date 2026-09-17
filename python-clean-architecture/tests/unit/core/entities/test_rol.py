import pytest

from app.core.entities.rol import Rol
from app.core.value_objects.id import ID
from app.core.value_objects.role_name import InvalidRoleNameError, RoleName


@pytest.fixture
def valid_data():
    return {
        "name": RoleName("admin"),
        "user_id": ID.generate(),
    }


def test_if_generates_unique_id_for_new_roles(valid_data):
    rol1 = Rol(**valid_data, id=ID.generate())
    rol2 = Rol(**valid_data, id=ID.generate())
    assert rol1.id != rol2.id


def test_if_raises_when_user_id_is_missing():
    with pytest.raises(TypeError):
        Rol(id=ID.generate(), name=RoleName("admin"))


@pytest.mark.parametrize(
    "invalid_name",
    [
        ("A"),  # too short, uppercase
        ("Admin"),  # uppercase
        ("admin admin"),  # space
        ("1admin"),  # starts with digit
        ("a" * 51),  # too long
        (""),  # empty
    ],
)
def test_if_raises_when_role_name_is_invalid(invalid_name):
    with pytest.raises(InvalidRoleNameError):
        RoleName(invalid_name)


@pytest.mark.parametrize("valid_name", [("admin"), ("super_admin"), ("role_1"), ("a" * 50)])
def test_if_accepts_valid_role_names(valid_name):
    assert RoleName(valid_name).value == valid_name


def test_if_rol_is_immutable(valid_data):
    rol = Rol(**valid_data, id=ID.generate())
    with pytest.raises(AttributeError):
        rol.name = RoleName("editor")  # type: ignore[misc]

    with pytest.raises(AttributeError):
        rol.user_id = ID.generate()  # type: ignore[misc]
