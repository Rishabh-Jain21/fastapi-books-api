import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth_header, create_admin_user, create_test_user, login_user


@pytest.mark.anyio
async def test_get_review_not_found(client: AsyncClient):
    response = await client.get("/reviews/999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Review not found"


@pytest.mark.anyio
async def test_patch_review_not_found(client: AsyncClient):
    await create_test_user(client)
    user_token = await login_user(
        client=client, username="testuser", password="testpassword123"
    )
    headers = auth_header(user_token)

    response = await client.patch(
        "/reviews/999", json={"content": "Updated content"}, headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Review not found"


@pytest.mark.anyio
async def test_patch_review_not_owner(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    user_1_header = auth_header(admin_token)
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=user_1_header,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Create a review by one user
    user1 = await create_test_user(client, "user1", "user1@example.com", "password123")

    user_1_token = await login_user(
        client,
        username=user1["username"],
        password="password123",
    )
    user_1_header = auth_header(user_1_token)

    # Add reviews for the book
    review_response = await client.post(
        f"/books/{book_id}/reviews",
        json={"rating": 4, "comment": "Review 1"},
        headers=user_1_header,
    )
    review_response_data = review_response.json()
    review_id = review_response_data["id"]

    # Create another user
    user2 = await create_test_user(client, "user2", "user2@example.com", "password123")

    user_2_token = await login_user(
        client,
        username=user2["username"],
        password="password123",
    )
    user_2_header = auth_header(user_2_token)

    # Attempt to update the review by a different user
    patch_response = await client.patch(
        f"/reviews/{review_id}",
        json={"comment": "Updated comment"},
        headers=user_2_header,
    )
    assert patch_response.status_code == 403


@pytest.mark.anyio
async def test_delete_review_not_owner(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    user_1_header = auth_header(admin_token)
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=user_1_header,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Create a review by one user
    user1 = await create_test_user(client, "user1", "user1@example.com", "password123")

    user_1_token = await login_user(
        client,
        username=user1["username"],
        password="password123",
    )
    user_1_header = auth_header(user_1_token)

    # Add reviews for the book
    review_response = await client.post(
        f"/books/{book_id}/reviews",
        json={"rating": 4, "comment": "Review 1"},
        headers=user_1_header,
    )
    review_response_data = review_response.json()
    review_id = review_response_data["id"]

    # Create another user
    user2 = await create_test_user(client, "user2", "user2@example.com", "password123")

    user_2_token = await login_user(
        client,
        username=user2["username"],
        password="password123",
    )
    user_2_header = auth_header(user_2_token)

    # Attempt to delete the review by a different user
    delete_response = await client.delete(
        f"/reviews/{review_id}",
        headers=user_2_header,
    )
    assert delete_response.status_code == 403


@pytest.mark.anyio
async def test_get_review_success(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)

    admin_token = await login_user(client, username="admin", password="admin")

    admin_header = auth_header(admin_token)

    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=admin_header,
    )

    book_id = response.json()["id"]

    # Create a review for the book
    response = await client.post(
        f"/books/{book_id}/reviews",
        json={"rating": 4, "comment": "Test review"},
        headers=admin_header,
    )
    assert response.status_code == 201
    review_id = response.json()["id"]

    # Get the review
    response = await client.get(f"/reviews/{review_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert "comment" in data
    assert "rating" in data


@pytest.mark.anyio
async def test_delete_review_success(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)

    admin_token = await login_user(client, username="admin", password="admin")

    admin_header = auth_header(admin_token)

    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=admin_header,
    )

    book_id = response.json()["id"]

    # Create a review for the book
    response = await client.post(
        f"/books/{book_id}/reviews",
        json={"rating": 4, "comment": "Test review"},
        headers=admin_header,
    )
    assert response.status_code == 201
    review_id = response.json()["id"]

    # Get the review
    response = await client.get(f"/reviews/{review_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id
    assert "comment" in data
    assert "rating" in data

    # Delete the review
    delete_response = await client.delete(
        f"/reviews/{review_id}",
        headers=admin_header,
    )
    assert delete_response.status_code == 204

    # Attempt to get the deleted review
    get_response = await client.get(f"/reviews/{review_id}")
    assert get_response.status_code == 404
