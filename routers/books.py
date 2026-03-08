from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/books", tags=["Books"])
ALLOWED_SORT_FIELDS = {"title", "author", "year", "created_at"}


@router.get("/", response_model=schemas.BookListResponse)
def get_books(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    author: str | None = Query(None),
    year: int | None = Query(None),
    search: str | None = Query(
        None, description="Case insensitive search by title of book"
    ),
    sort: str | None = Query(None),
    db: Session = Depends(get_db),
):
    book_query = db.query(models.Book).filter(models.Book.is_deleted == False)

    if author:
        book_query = book_query.filter(models.Book.author == author)

    if year is not None:
        book_query = book_query.filter(models.Book.year == year)

    if search:
        book_query = book_query.filter(models.Book.title.ilike(f"%{search}%"))

    if sort:
        desc = sort.startswith("-")
        field = sort[1:] if desc else sort

        if field in ALLOWED_SORT_FIELDS:
            column = getattr(models.Book, field)
            book_query = book_query.order_by(column.desc() if desc else column.asc())
    else:
        book_query = book_query.order_by(models.Book.id.asc())

    total = book_query.order_by(None).count()

    books = book_query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": books,
    }


@router.get("/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@router.post("/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(title=book.title, author=book.author, year=book.year)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.patch("/{book_id}", response_model=schemas.BookResponse)
def patch_book(
    book_id: int, book_updated: schemas.BookUpdate, db: Session = Depends(get_db)
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    updated_data = book_updated.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=schemas.BookResponse)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book or db_book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year

    db.commit()
    db.refresh(db_book)

    return db_book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):

    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book or db_book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.is_deleted = True
    db.commit()


@router.post("/{book_id}/reviews", response_model=schemas.ReviewResponse)
def create_review(
    book_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db)
):
    book = db.get(models.Book, book_id)

    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    book_review = models.Review(
        book_id=book_id, rating=review.rating, comment=review.comment
    )
    db.add(book_review)
    db.commit()
    db.refresh(book_review)
    return book_review


@router.get("/{book_id}/reviews", response_model=list[schemas.ReviewResponse])
def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)

    if not book or book.is_deleted:
        raise HTTPException(status_code=404, detail="Book not found")

    reviews = (
        db.query(models.Review)
        .filter(
            (models.Review.book_id == book_id) & (models.Review.is_deleted == False)
        )
        .all()
    )

    return reviews
