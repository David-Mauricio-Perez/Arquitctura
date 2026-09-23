from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.dtos.rol import CreateRolRequest, UpdateRol
from app.core.entities.rol import Rol
from app.core.entities.user import User
from app.core.exceptions import (
    InvalidRolError,
    RolAlreadyExistsError,
    RolNotFoundError,
    UserNotFoundError,
)
from app.core.usecases.rol import (
    CreateRolUsecase,
    DeleteRolUsecase,
    GetRolUsecase,
    UpdateRolUsecase,
)
from app.core.value_objects.email import Email
from app.core.value_objects.id import ID
from app.core.value_objects.password import Password
from app.core.value_objects.role_name import RoleName


@pytest.fixture
def create_rol_dto():
    user_id = str(uuid4())
    return CreateRolRequest(name="admin", user_id=user_id)


@pytest.fixture
def mock_user():
    return User(
        id=ID.generate(),
        name="Test",
        email=Email("test@test.com"),
        password=Password("hashed_password"),
    )


@pytest.fixture
def mock_rol():
    return Rol(id=ID.generate(), name=RoleName("admin"), user_id=ID.generate())


@pytest.fixture
def mock_rol_repo():
    """Create a mock rol repository."""
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_name = AsyncMock()
    repo.get_by_user_id = AsyncMock()
    repo.delete = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_user_repo():
    """Create a mock user repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    return repo


@pytest.fixture
def mock_rol_uow(mock_rol_repo, mock_user_repo):
    """Create a mock unit of work."""
    uow = MagicMock()
    uow.rol_repo = mock_rol_repo
    uow.user_repo = mock_user_repo
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow


async def test_if_creates_rol(mock_rol_uow, mock_user, mock_rol, create_rol_dto):
    mock_rol_uow.user_repo.get_by_id.return_value = mock_user
    mock_rol_uow.rol_repo.get_by_name.return_value = None
    mock_rol_uow.rol_repo.get_by_user_id.return_value = None

    use_case = CreateRolUsecase(uow=mock_rol_uow)
    result = await use_case.execute(create_rol_dto)

    assert result.name == create_rol_dto.name
    assert result.user_id == create_rol_dto.user_id
    assert isinstance(result.id, str)

    mock_rol_uow.rol_repo.save.assert_called_once()
    mock_rol_uow.rol_repo.get_by_name.assert_called_once()
    mock_rol_uow.rol_repo.get_by_user_id.assert_called_once()


async def test_if_raises_when_user_not_found(mock_rol_uow, create_rol_dto):
    mock_rol_uow.user_repo.get_by_id.return_value = None

    use_case = CreateRolUsecase(uow=mock_rol_uow)

    with pytest.raises(
        UserNotFoundError, match=f"User with ID {create_rol_dto.user_id} not found"
    ):
        await use_case.execute(create_rol_dto)

    mock_rol_uow.rol_repo.save.assert_not_called()


async def test_if_raises_when_rol_name_already_exists(
    mock_rol_uow, mock_user, mock_rol, create_rol_dto
):
    mock_rol_uow.user_repo.get_by_id.return_value = mock_user
    mock_rol_uow.rol_repo.get_by_name.return_value = mock_rol

    use_case = CreateRolUsecase(uow=mock_rol_uow)

    with pytest.raises(RolAlreadyExistsError, match=f"Rol with name {create_rol_dto.name}"):
        await use_case.execute(create_rol_dto)

    mock_rol_uow.rol_repo.save.assert_not_called()


async def test_if_raises_when_user_already_has_rol(
    mock_rol_uow, mock_user, mock_rol, create_rol_dto
):
    mock_rol_uow.user_repo.get_by_id.return_value = mock_user
    mock_rol_uow.rol_repo.get_by_name.return_value = None
    mock_rol_uow.rol_repo.get_by_user_id.return_value = mock_rol

    use_case = CreateRolUsecase(uow=mock_rol_uow)

    with pytest.raises(RolAlreadyExistsError, match="already has a rol"):
        await use_case.execute(create_rol_dto)

    mock_rol_uow.rol_repo.save.assert_not_called()


async def test_if_raises_when_rol_data_is_invalid(mock_rol_uow):
    use_case = CreateRolUsecase(uow=mock_rol_uow)

    invalid_name = CreateRolRequest(name="Invalid Name", user_id=str(uuid4()))
    with pytest.raises(InvalidRolError):
        await use_case.execute(invalid_name)

    invalid_user_id = CreateRolRequest(name="admin", user_id="not-a-uuid")
    with pytest.raises(InvalidRolError):
        await use_case.execute(invalid_user_id)

    mock_rol_uow.rol_repo.save.assert_not_called()


async def test_if_get_rol_by_id(mock_rol_repo, mock_rol):
    mock_rol_repo.get_by_id.return_value = mock_rol

    use_case = GetRolUsecase(rol_repo=mock_rol_repo)
    result = await use_case.execute(str(mock_rol.id))

    assert result.id == str(mock_rol.id)
    assert result.name == mock_rol.name.value
    assert result.user_id == str(mock_rol.user_id)
    mock_rol_repo.get_by_id.assert_called_once()


async def test_if_raises_when_getting_nonexisting_rol(mock_rol_repo):
    mock_rol_repo.get_by_id.return_value = None

    use_case = GetRolUsecase(rol_repo=mock_rol_repo)

    with pytest.raises(RolNotFoundError):
        await use_case.execute(str(uuid4()))

    mock_rol_repo.get_by_id.assert_called_once()


async def test_if_get_rol_by_user_id(mock_rol_repo, mock_rol):
    mock_rol_repo.get_by_user_id.return_value = mock_rol

    use_case = GetRolUsecase(rol_repo=mock_rol_repo)
    result = await use_case.execute_by_user_id(str(mock_rol.user_id))

    assert result.id == str(mock_rol.id)
    assert result.name == mock_rol.name.value
    assert result.user_id == str(mock_rol.user_id)
    mock_rol_repo.get_by_user_id.assert_called_once()


async def test_if_raises_when_getting_rol_by_nonexisting_user_id(mock_rol_repo):
    mock_rol_repo.get_by_user_id.return_value = None

    use_case = GetRolUsecase(rol_repo=mock_rol_repo)

    with pytest.raises(RolNotFoundError):
        await use_case.execute_by_user_id(str(uuid4()))

    mock_rol_repo.get_by_user_id.assert_called_once()



async def test_if_returns_false_when_deleting_nonexisting_rol(mock_rol_uow):
    mock_rol_uow.rol_repo.delete.return_value = False

    use_case = DeleteRolUsecase(uow=mock_rol_uow)
    result = await use_case.execute(str(uuid4()))

    assert result is False
    mock_rol_uow.rol_repo.delete.assert_called_once()


async def test_if_returns_true_when_deleting_existing_rol(mock_rol_uow):
    mock_rol_uow.rol_repo.delete.return_value = True

    use_case = DeleteRolUsecase(uow=mock_rol_uow)
    result = await use_case.execute(str(uuid4()))

    assert result is True
    mock_rol_uow.rol_repo.delete.assert_called_once()


async def test_if_updates_rol_name(mock_rol_uow, mock_rol):
    updated_rol = Rol(id=mock_rol.id, name=RoleName("editor"), user_id=mock_rol.user_id)

    mock_rol_uow.rol_repo.get_by_id.return_value = mock_rol
    mock_rol_uow.rol_repo.get_by_name.return_value = None
    mock_rol_uow.rol_repo.update.return_value = updated_rol

    use_case = UpdateRolUsecase(uow=mock_rol_uow)
    result = await use_case.execute(str(mock_rol.id), UpdateRol(name="editor"))

    assert result.name == "editor"
    assert result.id == str(mock_rol.id)
    assert result.user_id == str(mock_rol.user_id)
    mock_rol_uow.rol_repo.update.assert_called_once()


async def test_if_keeps_user_id_unchanged_when_updating(mock_rol_uow, mock_rol):
    mock_rol_uow.rol_repo.get_by_id.return_value = mock_rol
    mock_rol_uow.rol_repo.get_by_name.return_value = None
    mock_rol_uow.rol_repo.update.return_value = mock_rol

    use_case = UpdateRolUsecase(uow=mock_rol_uow)
    await use_case.execute(str(mock_rol.id), UpdateRol(name="editor"))

    called_rol = mock_rol_uow.rol_repo.update.call_args[0][0]
    assert called_rol.user_id == mock_rol.user_id


async def test_if_raises_when_updating_to_taken_name(mock_rol_uow, mock_rol):
    other_rol = Rol(id=ID.generate(), name=RoleName("editor"), user_id=ID.generate())

    mock_rol_uow.rol_repo.get_by_id.return_value = mock_rol
    mock_rol_uow.rol_repo.get_by_name.return_value = other_rol

    use_case = UpdateRolUsecase(uow=mock_rol_uow)

    with pytest.raises(RolAlreadyExistsError):
        await use_case.execute(str(mock_rol.id), UpdateRol(name="editor"))

    mock_rol_uow.rol_repo.update.assert_not_called()


async def test_if_returns_error_when_updating_nonexisting_rol(mock_rol_uow):
    mock_rol_uow.rol_repo.get_by_id.return_value = None

    use_case = UpdateRolUsecase(uow=mock_rol_uow)

    with pytest.raises(RolNotFoundError):
        await use_case.execute(str(uuid4()), UpdateRol(name="editor"))

    mock_rol_uow.rol_repo.update.assert_not_called()
