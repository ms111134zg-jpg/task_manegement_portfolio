import pytest
from httpx import AsyncClient

async def test_create_user(client: AsyncClient):
    """ユーザー作成の正常系"""
    response = await client.post("/api/users", json={
        "name": "テストユーザー",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "テストユーザー"
    assert data["email"] == "test@example.com"
    assert "id" in data

async def test_create_user_duplicate_email(client: AsyncClient):
    """同じメールアドレスで2回作成すると409になる"""
    payload = {"name": "ユーザーA", "email": "dup@example.com"}
    await client.post("/api/users", json=payload)
    response = await client.post("/api/users", json=payload)
    assert response.status_code == 409

async def test_create_user_invalid_email(client: AsyncClient):
    """不正なメールアドレスは422になる"""
    response = await client.post("/api/users", json={
        "name": "ユーザーB",
        "email": "not-an-email"
    })
    assert response.status_code == 422

async def test_get_users(client: AsyncClient):
    """ユーザー一覧が取得できる"""
    await client.post("/api/users", json={
        "name": "ユーザーC",
        "email": "c@example.com"
    })
    response = await client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "c@example.com"