import pytest

from app.core.entities.user import User
from app.core.value_objects.email import Email, InvalidEmailError
from app.core.value_objects.id import ID
from app.core.value_objects.password import InvalidPasswordError, Password


@pytest.fixture
def valid_data():
    return {
        "name": "Test",
        "email": Email("test@gmail.com"),
        "password": Password("password"),
    }


def test_if_generates_unique_id_for_new_users(valid_data):
    user1 = User(**valid_data, id=ID.generate())
    user2 = User(**valid_data, id=ID.generate())
    assert user1.id != user2.id


def test_if_raises_when_password_has_less_than_eight_characters():
    with pytest.raises(InvalidPasswordError):
        Password("small")


def test_if_raises_when_password_has_has_more_than_hundred_characters():
    with pytest.raises(InvalidPasswordError):
        Password("p" * 101)


@pytest.mark.parametrize(
    "invalid_email",
    [
        ("invalid"),
        ("@"),
        ("@.com"),
        ("bla.com"),
        ("@bla.com"),
    ],
)
def test_if_raises_when_email_is_invalid(invalid_email):
    with pytest.raises(InvalidEmailError):
        Email(invalid_email)


def test_if_user_can_have_assigned_rol_1_to_1(valid_data):
    from app.core.entities.rol import Rol
    from app.core.value_objects.role_name import RoleName

    user_id = ID.generate()
    rol = Rol(id=ID.generate(), name=RoleName("admin"), user_id=user_id)
    user = User(**valid_data, id=user_id, rol=rol)

    assert user.rol is not None
    assert user.rol.user_id == user.id
    assert user.rol.name.value == "admin"


def test_if_raises_when_assigned_rol_belongs_to_different_user(valid_data):
    from app.core.entities.rol import Rol
    from app.core.exceptions import InvalidUserError
    from app.core.value_objects.role_name import RoleName

    user_id = ID.generate()
    different_user_id = ID.generate()
    rol = Rol(id=ID.generate(), name=RoleName("admin"), user_id=different_user_id)

    with pytest.raises(InvalidUserError, match="Assigned rol must belong to this user"):
        User(**valid_data, id=user_id, rol=rol)

