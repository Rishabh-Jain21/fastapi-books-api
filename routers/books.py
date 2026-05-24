from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas
from auth import get_current_user, require_role
from database import get_db

router = APIRouter(prefix="/books", tags=["Books"])
ALLOWED_SORT_FIELDS = {"title", "author", "year", "created_at"}


@router.get(
    "/", response_model=schemas.BookListResponse, status_code=status.HTTP_200_OK
)
async def get_books(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    author: str | None = Query(None),
    year: int | None = Query(None),
    search: str | None = Query(
        None, description="Case insensitive search by title of book"
    ),
    sort: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    book_query = (
        select(
            models.Book.id,
            models.Book.title,
            models.Book.author,
            models.Book.year,
            func.count(models.Review.id).label("review_count"),
            func.coalesce(func.avg(models.Review.rating), 0).label("average_rating"),
        )
        .filter(models.Book.is_deleted.is_(False))
        .outerjoin(
            models.Review,
            (models.Review.book_id == models.Book.id)
            & (models.Review.is_deleted.is_(False)),
        )
        .group_by(models.Book.id)
    )

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

    count_result = await db.execute(
        select(func.count()).select_from(book_query.order_by(None).subquery())
    )

    total = count_result.scalar_one() or 0

    books_result = await db.execute(book_query.offset(offset).limit(limit))

    books = books_result.all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": books,
    }


@router.get(
    "/{book_id}", response_model=schemas.BookResponse, status_code=status.HTTP_200_OK
)
async def get_book(book_id: int = Path(gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            models.Book.id,
            models.Book.title,
            models.Book.author,
            models.Book.year,
            func.count(models.Review.id).label("review_count"),
            func.coalesce(func.avg(models.Review.rating), 0).label("average_rating"),
        )
        .filter(models.Book.is_deleted.is_(False), models.Book.id == book_id)
        .outerjoin(
            models.Review,
            (models.Review.book_id == models.Book.id)
            & (models.Review.is_deleted.is_(False)),
        )
        .group_by(models.Book.id)
    )

    book = result.one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


@router.post(
    "/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED
)
async def create_book(
    book: schemas.BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    new_book = models.Book(title=book.title, author=book.author, year=book.year)

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return new_book


@router.patch(
    "/{book_id}",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def patch_book(
    book_updated: schemas.BookUpdate,
    book_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id))

    book = result.scalars().first()

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    updated_data = book_updated.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(book, key, value)
    await db.commit()
    await db.refresh(book)
    return book


@router.put(
    "/{book_id}",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def update_book(
    book: schemas.BookCreate,
    book_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):
    result = await db.execute(select(models.Book).filter(models.Book.id == book_id))

    db_book = result.scalars().first()

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

    await db.commit()
    await db.refresh(db_book)

    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(require_role("admin")),
):

    result = await db.execute(select(models.Book).filter(models.Book.id == book_id))

    db_book = result.scalars().first()
    if not db_book or db_book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db_book.is_deleted = True
    await db.commit()


@router.post(
    "/{book_id}/reviews",
    response_model=schemas.ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review: schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    book_id: int = Path(gt=0),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    book = await db.get(models.Book, book_id)
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
    await db.commit()
    await db.refresh(book_review, attribute_names=["user"])
    return book_review


@router.get(
    "/{book_id}/reviews",
    response_model=schemas.ReviewListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_book_reviews(
    book_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    rating: int | None = None,
    search: str | None = None,
    sort: str | None = None,
):
    book = await db.get(models.Book, book_id)

    if not book or book.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    review_query = select(models.Review).filter(
        (models.Review.book_id == book_id) & (models.Review.is_deleted.is_(False))
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

    total_result = await db.execute(
        select(func.count()).select_from(review_query.order_by(None).subquery())
    )

    total = total_result.scalar_one()

    reviews_result = await db.execute(
        review_query.offset(offset)
        .limit(limit)
        .options(selectinload(models.Review.user))
    )
    reviews = reviews_result.scalars().all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": reviews,
    }
