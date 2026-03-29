from pydantic import BaseModel, ConfigDict, EmailStr


class BookCreate(BaseModel):
    title: str
    author: str
    year: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "year": 1960,
            }
        }
    )


class BookResponse(BookCreate):
    id: int

    model_config = ConfigDict(from_attributes=True, json_schema_extra=None)


class BookListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[BookResponse]


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None


class ReviewCreate(BaseModel):
    rating: int
    comment: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"rating": 4, "comment": "This is a good book"}}
    )


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[ReviewResponse]


class ReviewUpdate(BaseModel):
    rating: int | None = None
    comment: str | None = None


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    user_id: int
    role: str
