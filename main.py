from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from database import get_db
import schemas

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Book Review API running"}


@app.get("/books", response_model=list[schemas.BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books


@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.post("/books", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(title=book.title, author=book.author, year=book.year)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year

    db.commit()
    db.refresh(db_book)

    return db_book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):

    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()

    return {"message": "Book deleted successfully"}


@app.get("/hello")
def say_hello():
    return {"message": "Hello User"}


@app.get("/search")
def search_books(author: str, year: int):
    return {"author": author, "year": year}


@app.get("/db-test")
def db_test(db: Session = Depends(get_db)):
    return {"message": "DB connected"}
