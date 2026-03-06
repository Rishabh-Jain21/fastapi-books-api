from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db


class Book(BaseModel):
    title: str
    author: str
    year: int
    price: float


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Book Review API running"}


@app.get("/books")
def get_books():
    return [{"title": "The Hobbit"}, {"title": "Harry Potter"}]


@app.get("/books/{book_id}")
def get_book(book_id: int):
    return {"book_id": book_id}


@app.post("/books")
def create_book(book: Book):
    return {"message": "Book created", "book": book}


@app.get("/hello")
def say_hello():
    return {"message": "Hello User"}


@app.get("/search")
def search_books(author: str, year: int):
    return {"author": author, "year": year}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    return {"message": "DB connected"}
