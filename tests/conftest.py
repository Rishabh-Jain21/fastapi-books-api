import os

# Set environment variables before importing the app or database.
# This ensures tests use a temporary in-memory database and a fixed secret key,
# so they do not depend on development or production configuration.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = (
    "cddc32cab571f0c1cdcf8adcdd5b3b13d618516919232983568fe5e381256dcb"
)


from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import create_app

# Register anyio with pytest so async fixtures and tests run correctly.
pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# If using in-memory use StaticPool else use NullPool for sqlite file based database. For other databases, you can remove the poolclass argument or set it to the default.
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        # poolclass=NullPool,
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session

            # this is for sqlite, which does not support nested transactions, so we need to manually delete data after each test. For databases that support nested transactions, the rollback will automatically undo any changes made during the test.
            # Remove these lines if you switch to a database that supports nested transactions (like PostgreSQL or MySQL).
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(delete(table))
            await session.commit()

        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:
    async def override_get_db():
        yield db_session

    app = create_app()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def rate_limited_client(
    db_session: AsyncSession, monkeypatch
) -> AsyncGenerator[AsyncClient]:
    monkeypatch.setenv("ENABLE_RATE_LIMITING", "true")

    async def override_get_db():
        yield db_session

    app = create_app()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpassword123",
) -> dict:
    response = await client.post(
        "/users/",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    return response.json()


async def create_admin_user(db_session: AsyncSession):

    # Inline import to avoid circular dependency issues, since auth.py imports models.py and conftest.py imports both auth.py and models.py.
    from auth import hash_password
    from models import User

    admin_user = User(
        username="admin",
        email="admin@gmail.com",
        password_hash=hash_password("admin"),
        role="admin",
    )

    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)


async def login_user(
    client: AsyncClient,
    username: str = "testuser",
    password: str = "testpassword123",
) -> str:
    response = await client.post(
        "/users/token",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
