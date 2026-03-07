from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    year: int


class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[BookResponse]


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
