from uuid import uuid4

import pytest


@pytest.fixture
def rol_route():
    return "/api/v1/roles"


@pytest.fixture
def user_route():
    return "/api/v1/users"


@pytest.fixture
def create_user_payload():
    return {
        "name": "Test",
        "email": "test@gmail.com",
        "password": "password",
    }


@pytest.fixture
def create_rol_payload():
    return {"name": "admin", "user_id": None}


async def test_get_rol_not_found(client, rol_route):
    response = await client.get(f"{rol_route}/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "Rol not found"}


async def test_create_rol_user_not_found(client, rol_route):
    response = await client.post(rol_route, json={"name": "admin", "user_id": str(uuid4())})
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "User not found"}


async def test_create_rol_invalid_name(client, rol_route):
    response = await client.post(
        rol_route, json={"name": "Invalid Name", "user_id": str(uuid4())}
    )
    data, status_code = response.json(), response.status_code

    assert status_code == 400
    assert "detail" in data


async def test_create_rol_and_get_successfully(
    client, rol_route, user_route, create_user_payload, create_rol_payload
):
    create_user_response = await client.post(user_route, json=create_user_payload)
    user_id = create_user_response.json()["id"]

    create_rol_payload["user_id"] = user_id
    create_response = await client.post(rol_route, json=create_rol_payload)
    created, status_code = create_response.json(), create_response.status_code

    assert status_code == 201
    assert created["name"] == create_rol_payload["name"]
    assert created["user_id"] == user_id

    get_response = await client.get(f"{rol_route}/{created['id']}")
    fetched, status_code = get_response.json(), get_response.status_code

    assert status_code == 200
    assert fetched["name"] == created["name"]
    assert fetched["user_id"] == created["user_id"]

    # Verify 1:1 lookup by user_id
    get_by_user_resp = await client.get(f"{rol_route}/user/{user_id}")
    by_user_data, by_user_status = get_by_user_resp.json(), get_by_user_resp.status_code
    assert by_user_status == 200
    assert by_user_data["id"] == created["id"]
    assert by_user_data["name"] == created["name"]
    assert by_user_data["user_id"] == user_id


async def test_get_rol_by_user_id_not_found(client, rol_route):
    response = await client.get(f"{rol_route}/user/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "Rol not found for user"}



async def test_create_rol_conflict_duplicated_name(
    client, rol_route, user_route, create_user_payload, create_rol_payload
):
    create_user_response = await client.post(user_route, json=create_user_payload)
    user_id = create_user_response.json()["id"]
    create_rol_payload["user_id"] = user_id
    await client.post(rol_route, json=create_rol_payload)

    # Same rol name for another user
    another_user_payload = {**create_user_payload, "email": "another@gmail.com"}
    another_user_response = await client.post(user_route, json=another_user_payload)
    another_user_id = another_user_response.json()["id"]

    response = await client.post(
        rol_route, json={"name": create_rol_payload["name"], "user_id": another_user_id}
    )
    data, status_code = response.json(), response.status_code

    assert status_code == 409
    assert data == {"detail": "Rol already exists"}


async def test_create_rol_conflict_user_already_has_rol(
    client, rol_route, user_route, create_user_payload, create_rol_payload
):
    create_user_response = await client.post(user_route, json=create_user_payload)
    user_id = create_user_response.json()["id"]
    create_rol_payload["user_id"] = user_id
    await client.post(rol_route, json=create_rol_payload)

    response = await client.post(rol_route, json={"name": "editor", "user_id": user_id})
    data, status_code = response.json(), response.status_code

    assert status_code == 409
    assert data == {"detail": "Rol already exists"}


async def test_patch_rol_not_found(client, rol_route):
    response = await client.patch(f"{rol_route}/{uuid4()}", json={"name": "editor"})
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "Rol not found"}


async def test_patch_rol_name_successfully(
    client, rol_route, user_route, create_user_payload, create_rol_payload
):
    create_user_response = await client.post(user_route, json=create_user_payload)
    user_id = create_user_response.json()["id"]
    create_rol_payload["user_id"] = user_id
    create_response = await client.post(rol_route, json=create_rol_payload)
    rol_id = create_response.json()["id"]

    patch_response = await client.patch(f"{rol_route}/{rol_id}", json={"name": "editor"})

    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "editor"
    assert patch_response.json()["user_id"] == user_id


async def test_delete_rol_not_found(client, rol_route):
    response = await client.delete(f"{rol_route}/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "Rol not found"}


async def test_delete_rol_successfully(
    client, rol_route, user_route, create_user_payload, create_rol_payload
):
    create_user_response = await client.post(user_route, json=create_user_payload)
    user_id = create_user_response.json()["id"]
    create_rol_payload["user_id"] = user_id
    create_response = await client.post(rol_route, json=create_rol_payload)
    rol_id = create_response.json()["id"]

    delete_response = await client.delete(f"{rol_route}/{rol_id}")

    assert delete_response.status_code == 204

    get_response = await client.get(f"{rol_route}/{rol_id}")
    assert get_response.status_code == 404
