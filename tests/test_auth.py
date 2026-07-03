import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_admin_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@test.com",
            "username": "testadmin",
            "password": "testpass123",
            "full_name": "Test Admin",
            "role": "admin",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_no_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": "nonexistent@test.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_public_endpoints(client: AsyncClient):
    response = await client.get("/api/v1/authors")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_books_no_auth(client: AsyncClient):
    response = await client.get("/api/v1/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
