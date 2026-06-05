from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import configure_mappers

from config import get_settings
from database import Base, engine, get_db
from middleware import RateLimitMiddleware
from routers import books, reviews, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    configure_mappers()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:

    app = FastAPI(
        title="Books API",
        description="Api where admin can add books and authenticated users can review the books",
        lifespan=lifespan,
    )
    settings = get_settings()

    if settings.enable_rate_limiting:
        app.add_middleware(RateLimitMiddleware)

    app.include_router(books.router)
    app.include_router(reviews.router)
    app.include_router(users.router)

    @app.get("/")
    async def root():
        return {"message": "Book Review API running"}

    @app.get("/hello")
    async def say_hello():
        return {"message": "Hello User"}

    @app.get("/search")
    async def search_books(author: str, year: int):
        return {"author": author, "year": year}

    @app.get("/db-test")
    async def db_test(db: AsyncSession = Depends(get_db)):
        return {"message": "DB connected"}

    return app


app = create_app()
