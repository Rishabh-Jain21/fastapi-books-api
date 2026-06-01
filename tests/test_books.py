import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth_header, create_admin_user, create_test_user, login_user


@pytest.mark.anyio
async def test_get_books_empty(client: AsyncClient) -> None:
    response = await client.get("/books/")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.anyio
async def test_get_book_not_found(client: AsyncClient):
    response = await client.get("/books/999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Book not found"


@pytest.mark.anyio
async def test_not_create_book_not_admin_user(client: AsyncClient) -> None:

    user = await create_test_user(
        client, "username", "email@example.com", "password123"
    )
    user_token = await login_user(
        client,
        username=user["username"],
        password="password123",
    )

    headers = auth_header(user_token)

    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_not_create_book_not_authenticated(client: AsyncClient) -> None:
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_book_as_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"
    assert response.json()["author"] == "Test Author"


@pytest.mark.anyio
async def test_update_book_as_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:

    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    # Create a book to update
    response = await client.post(
        "/books/",
        json={"title": "Original Title", "author": "Original Author", "year": 2020},
        headers=headers,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Update the book
    update_response = await client.put(
        f"/books/{book_id}",
        json={"title": "Updated Title", "author": "Updated Author", "year": 2021},
        headers=headers,
    )
    assert update_response.status_code == 201
    updated_book = update_response.json()
    assert updated_book["title"] == "Updated Title"
    assert updated_book["author"] == "Updated Author"


@pytest.mark.anyio
async def test_patch_book_as_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:

    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    # Create a book to update
    response = await client.post(
        "/books/",
        json={"title": "Original Title", "author": "Original Author", "year": 2020},
        headers=headers,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Patch the book (only update the title)
    patch_response = await client.patch(
        f"/books/{book_id}",
        json={"title": "Patched Title"},
        headers=headers,
    )
    assert patch_response.status_code == 201
    patched_book = patch_response.json()
    assert patched_book["title"] == "Patched Title"
    assert patched_book["author"] == "Original Author"


@pytest.mark.anyio
async def test_patch_book_not_found(client: AsyncClient, db_session: AsyncSession):

    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    patch_response = await client.patch(
        "/books/999",
        json={"title": "Nonexistent Book"},
        headers=headers,
    )
    assert patch_response.status_code == 404
    assert patch_response.json()["detail"] == "Book not found"


@pytest.mark.anyio
async def test_update_book_not_found(client: AsyncClient, db_session: AsyncSession):

    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    update_response = await client.put(
        "/books/999",
        json={"title": "Nonexistent Book", "author": "No Author", "year": 2021},
        headers=headers,
    )
    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Book not found"


@pytest.mark.anyio
async def test_get_books_with_data(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    # Create multiple books
    for i in range(20):
        response = await client.post(
            "/books/",
            json={
                "title": f"Book {i + 1}",
                "author": f"Author {i + 1}",
                "year": 2000 + i,
            },
            headers=headers,
        )
        assert response.status_code == 201

    # Get the list of books
    get_response = await client.get("/books/")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["total"] == 20
    assert len(data["data"]) == 10
    assert data["limit"] == 10
    assert data["offset"] == 0

    get_response = await client.get("/books/?limit=5&offset=5")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["total"] == 20
    assert len(data["data"]) == 5
    assert data["limit"] == 5
    assert data["offset"] == 5


@pytest.mark.anyio
async def test_create_book_missing_fields(
    client: AsyncClient, db_session: AsyncSession
):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    response = await client.post(
        "/books/",
        json={"author": "Test Author", "year": 2021},
        headers=headers,
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_empty_book_reviews(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    # Create a book
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=headers,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    # Get the book details and check reviews
    get_response = await client.get(f"/books/{book_id}")
    assert get_response.status_code == 200
    book_data = get_response.json()
    assert book_data["review_count"] == 0
    assert book_data["average_rating"] == 0


@pytest.mark.anyio
async def test_create_user_review(client: AsyncClient, db_session: AsyncSession):
    await create_admin_user(db_session)
    admin_token = await login_user(client, username="admin", password="admin")

    headers = auth_header(admin_token)

    # Create a book
    response = await client.post(
        "/books/",
        json={"title": "Test Book", "author": "Test Author", "year": 2021},
        headers=headers,
    )
    assert response.status_code == 201
    book_id = response.json()["id"]

    new_user = await create_test_user(client)

    user_token = await login_user(
        client,
        username=new_user["username"],
        password="testpassword123",
    )
    # Add reviews for the book
    headers = auth_header(user_token)
    review_response = await client.post(
        f"/books/{book_id}/reviews",
        json={"rating": 4, "comment": "Review 1"},
        headers=headers,
    )
    assert review_response.status_code == 201

    # Get the book details and check reviews
    get_response = await client.get(f"/books/{book_id}/reviews")
    assert get_response.status_code == 200
    book_data = get_response.json()
    print(book_data)
    assert book_data["total"] == 1
    assert book_data["limit"] == 10
    assert book_data["offset"] == 0
