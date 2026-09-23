"""Tests de la capa API para el recurso público/privado /categories."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _register_and_login(client: AsyncClient, email: str = "cat_admin@example.com") -> str:
    user_payload = {
        "email": email,
        "full_name": "Category Admin",
        "password": "PasswordSegura123!",
    }
    await client.post("/api/v1/auth/register", json=user_payload)
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "PasswordSegura123!"},
    )
    return login_response.json()["access_token"]


async def test_list_categories_unauthenticated_returns_200(client: AsyncClient):
    """Verifica que el listado de categorías es público (sin Authorization header)."""
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["page"] == 1


async def test_get_category_unauthenticated_returns_200(client: AsyncClient):
    """Verifica que consultar una categoría específica por ID es público."""
    token = await _register_and_login(client, "creator_public@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": "Tecnología", "description": "Artículos tech", "color": "#10B981"},
        headers=headers,
    )
    cat_id = create_resp.json()["id"]

    # Consulta anónima sin cabecera de autenticación
    anon_resp = await client.get(f"/api/v1/categories/{cat_id}")
    assert anon_resp.status_code == 200
    body = anon_resp.json()
    assert body["id"] == cat_id
    assert body["name"] == "Tecnología"
    assert body["color"] == "#10B981"


async def test_create_category_unauthenticated_returns_401(client: AsyncClient):
    """Verifica que la mutación (crear) exige autenticación."""
    response = await client.post(
        "/api/v1/categories",
        json={"name": "No Autorizado", "description": "Debe fallar"},
    )
    assert response.status_code == 401


async def test_create_category_authenticated_returns_201(client: AsyncClient):
    """Verifica la creación exitosa con token."""
    token = await _register_and_login(client, "creator_auth@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "Trabajo", "description": "Tareas laborales", "color": "#3B82F6"}
    response = await client.post("/api/v1/categories", json=payload, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] is not None
    assert body["name"] == "Trabajo"
    assert body["color"] == "#3B82F6"
    assert body["is_active"] is True


async def test_create_category_duplicate_name_returns_409(client: AsyncClient):
    """Verifica la restricción de unicidad del nombre de categoría (409 Conflict)."""
    token = await _register_and_login(client, "creator_dup@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"name": "Finanzas", "description": "Gastos y presupuestos"}
    resp1 = await client.post("/api/v1/categories", json=payload, headers=headers)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/categories", json=payload, headers=headers)
    assert resp2.status_code == 409


async def test_update_category_patch_authenticated_returns_200(client: AsyncClient):
    """Verifica la actualización parcial con PATCH."""
    token = await _register_and_login(client, "creator_patch@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": "Estudio", "description": "Cursos"},
        headers=headers,
    )
    cat_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/categories/{cat_id}",
        json={"description": "Cursos y certificaciones", "color": "#8B5CF6"},
        headers=headers,
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["name"] == "Estudio"
    assert body["description"] == "Cursos y certificaciones"
    assert body["color"] == "#8B5CF6"


async def test_delete_category_authenticated_returns_204(client: AsyncClient):
    """Verifica la eliminación de categorías (204 No Content) y posterior 404."""
    token = await _register_and_login(client, "creator_del@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/categories",
        json={"name": "Temporal"},
        headers=headers,
    )
    cat_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verificar que ya no existe (públicamente)
    get_resp = await client.get(f"/api/v1/categories/{cat_id}")
    assert get_resp.status_code == 404


async def test_get_nonexistent_category_returns_404(client: AsyncClient):
    """Verifica 404 para categoría inexistente."""
    response = await client.get("/api/v1/categories/99999")
    assert response.status_code == 404
