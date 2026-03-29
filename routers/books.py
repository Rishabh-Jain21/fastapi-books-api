from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session, selectinload
from database import get_db
import models
import schemas
from auth import require_role

router = APIRouter(prefix="/books", tags=["Books"])
ALLOWED_SORT_FIELDS = {"title", "author", "year", "created_at"}


@router.get(
    "/", response_model=schemas.BookListResponse, status_code=status.HTTP_200_OK
)
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

    if author is not None:
        book_query = book_query.filter(models.Book.author == author)

    if year is not None:
        book_query = book_query.filter(models.Book.year == year)

    if search:
        search = search.strip()
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


@router.get(
    "/{book_id}", response_model=schemas.BookResponse, status_code=status.HTTP_200_OK
)
def get_book(book_id: int = Path(gt=0), db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


@router.post(
    "/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED
)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    new_book = models.Book(title=book.title, author=book.author, year=book.year)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.patch(
    "/{book_id}",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def patch_book(
    book_updated: schemas.BookUpdate,
    book_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    updated_data = book_updated.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.put(
    "/{book_id}",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def update_book(
    book: schemas.BookCreate,
    book_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book or db_book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )

    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year

    db.commit()
    db.refresh(db_book)

    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):

    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not db_book or db_book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db_book.is_deleted = True
    db.commit()


@router.post(
    "/{book_id}/reviews",
    response_model=schemas.ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    book_id: int = Path(gt=0),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    book = db.get(models.Book, book_id)

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    book_review = models.Review(
        book_id=book_id,
        rating=review.rating,
        comment=review.comment,
        user_id=current_user.user_id,
    )
    db.add(book_review)
    db.commit()
    db.refresh(book_review)
    return book_review


@router.get(
    "/{book_id}/reviews",
    response_model=schemas.ReviewListResponse,
    status_code=status.HTTP_200_OK,
)
def get_book_reviews(
    book_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    rating: int | None = None,
    search: str | None = None,
    sort: str | None = None,
):
    book = db.get(models.Book, book_id)

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    review_query = db.query(models.Review).filter(
        (models.Review.book_id == book_id) & (models.Review.is_deleted == False)
    )

    if rating is not None:
        review_query = review_query.filter(models.Review.rating == rating)

    if search:
        review_query = review_query.filter(models.Review.comment.ilike(f"%{search}%"))

    if sort:
        desc = sort.startswith("-")
        field = sort[1:] if desc else sort

        if field in {"rating"}:
            column = getattr(models.Review, field)
            review_query = review_query.order_by(
                column.desc() if desc else column.asc()
            )
        else:
            review_query = review_query.order_by(models.Review.id.asc())
    else:
        review_query = review_query.order_by(models.Review.id.asc())

    total = review_query.order_by(None).count()

    reviews = (
        review_query.offset(offset)
        .limit(limit)
        .options(selectinload(models.Review.user))
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": reviews,
    }
