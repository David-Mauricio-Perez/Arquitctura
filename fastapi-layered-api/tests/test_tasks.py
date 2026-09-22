"""Tests de la capa API para el nuevo recurso protegido /tasks."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str, password: str = "SuperSecreta123") -> str:
    user_payload = {
        "email": email,
        "full_name": "Test User",
        "password": password,
    }
    await client.post("/api/v1/auth/register", json=user_payload)
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return login_response.json()["access_token"]


async def test_create_task_unauthenticated_returns_401(client: AsyncClient):
    response = await client.post("/api/v1/tasks", json={"title": "Tarea sin auth"})
    assert response.status_code == 401


async def test_create_task_authenticated_returns_201(client: AsyncClient):
    token = await _register_and_login(client, "user_create_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    task_payload = {
        "title": "Aprender FastAPI Layered Architecture",
        "description": "Estudiar routers, services y repositories",
        "status": "pending",
        "priority": "high",
    }
    response = await client.post("/api/v1/tasks", json=task_payload, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["title"] == task_payload["title"]
    assert body["description"] == task_payload["description"]
    assert body["status"] == "pending"
    assert body["priority"] == "high"
    assert "owner_id" in body


async def test_get_task_by_id_returns_200(client: AsyncClient):
    token = await _register_and_login(client, "user_get_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Comprar cafe", "priority": "low"},
        headers=headers,
    )
    task_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Comprar cafe"


async def test_user_cannot_access_or_modify_another_users_task_returns_403(client: AsyncClient):
    # Usuario 1 crea una tarea
    token_1 = await _register_and_login(client, "owner_task@example.com")
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Tarea privada del usuario 1"},
        headers=headers_1,
    )
    task_id = create_resp.json()["id"]

    # Usuario 2 intenta acceder a la tarea del usuario 1
    token_2 = await _register_and_login(client, "attacker_task@example.com")
    headers_2 = {"Authorization": f"Bearer {token_2}"}

    # 1. Intento de lectura (BOLA)
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers_2)
    assert get_resp.status_code == 403

    # 2. Intento de modificación (BOLA)
    patch_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Título alterado"},
        headers=headers_2,
    )
    assert patch_resp.status_code == 403

    # 3. Intento de eliminación (BOLA)
    del_resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=headers_2)
    assert del_resp.status_code == 403


async def test_get_nonexistent_task_returns_404(client: AsyncClient):
    token = await _register_and_login(client, "user_404_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/tasks/99999", headers=headers)
    assert response.status_code == 404


async def test_list_tasks_is_paginated_and_filtered(client: AsyncClient):
    token = await _register_and_login(client, "user_list_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear 3 tareas: 2 pending y 1 completed
    await client.post("/api/v1/tasks", json={"title": "T1", "status": "pending"}, headers=headers)
    await client.post("/api/v1/tasks", json={"title": "T2", "status": "pending"}, headers=headers)
    await client.post("/api/v1/tasks", json={"title": "T3", "status": "completed"}, headers=headers)

    # Listar todas con paginación
    resp_all = await client.get("/api/v1/tasks?page=1&page_size=10", headers=headers)
    assert resp_all.status_code == 200
    body_all = resp_all.json()
    assert body_all["total"] == 3
    assert len(body_all["items"]) == 3

    # Filtrar por status=completed
    resp_completed = await client.get("/api/v1/tasks?status=completed", headers=headers)
    assert resp_completed.status_code == 200
    body_completed = resp_completed.json()
    assert body_completed["total"] == 1
    assert body_completed["items"][0]["title"] == "T3"


async def test_update_task_partial_patch_returns_200(client: AsyncClient):
    token = await _register_and_login(client, "user_patch_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Tarea inicial", "status": "pending", "priority": "low"},
        headers=headers,
    )
    task_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "completed", "priority": "high"},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["status"] == "completed"
    assert body["priority"] == "high"
    assert body["title"] == "Tarea inicial"  # No fue alterado


async def test_delete_task_returns_204_and_then_404(client: AsyncClient):
    token = await _register_and_login(client, "user_delete_task@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/tasks",
        json={"title": "Tarea para eliminar"},
        headers=headers,
    )
    task_id = create_resp.json()["id"]

    # Borrado exitoso
    del_resp = await client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verificar que ya no existe
    get_resp = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_resp.status_code == 404
