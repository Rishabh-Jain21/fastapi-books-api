import pytest
from httpx import AsyncClient

from tests.conftest import create_test_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):

    await create_test_user(
        client,
        username="testuser1",
        email="test1@example.com",
        password="testuser1password",
    )

    response = await client.post(
        "/users/",
        json={
            "username": "different_user",
            "email": "test1@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.anyio
async def test_user_login_success(client: AsyncClient):
    await create_test_user(
        client,
        username="testuser2",
        email="test2@example.com",
        password="testuser2password",
    )

    response = await client.post(
        "/users/token",
        data={
            "username": "testuser2",
            "password": "testuser2password",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_user_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/users/token",
        data={
            "username": "nonexistentuser",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_user_login_wrong_password(client: AsyncClient):
    await create_test_user(
        client,
        username="testuser3",
        email="test3@example.com",
        password="testuser3password",
    )

    response = await client.post(
        "/users/token",
        data={
            "username": "testuser3",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


@pytest.mark.anyio
async def test_user_login_wrong_username(client: AsyncClient):
    await create_test_user(
        client,
        username="testuser31",
        email="test31@example.com",
        password="testuser3password",
    )

    response = await client.post(
        "/users/token",
        data={
            "username": "nonexistentuser",
            "password": "testuser3password",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"
