from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import schemas

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=list[schemas.BookResponse])
def get_books(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    author: str | None = Query(None),
    year: int | None = Query(None),
    db: Session = Depends(get_db),
):
    book_query = db.query(models.Book)

    if author:
        book_query = book_query.filter(models.Book.author == author)

    if year is not None:
        book_query = book_query.filter(models.Book.year == year)

    books = book_query.offset(offset).limit(limit).all()

    return books


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(title=book.title, author=book.author, year=book.year)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.put("/{book_id}", response_model=schemas.BookResponse)
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


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):

    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()

    return {"message": "Book deleted successfully"}
