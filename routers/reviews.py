from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas
from auth import check_owner_or_admin, get_current_user
from database import get_db

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get(
    "/{review_id}",
    response_model=schemas.ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def get_review(review_id: int = Path(gt=0), db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(models.Review)
        .where(models.Review.id == review_id, models.Review.is_deleted.is_(False))
        .options(selectinload(models.Review.user))
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    return review


@router.patch(
    "/{review_id}",
    response_model=schemas.ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def patch_review(
    payload: schemas.ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    review_id: int = Path(gt=0),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(models.Review)
        .filter(models.Review.id == review_id, models.Review.is_deleted.is_(False))
        .options(selectinload(models.Review.user))
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    check_owner_or_admin(review.user_id, current_user)

    updated_data = payload.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(review, key, value)

    await db.commit()
    await db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int = Path(gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(models.Review).filter(
            models.Review.id == review_id, models.Review.is_deleted.is_(False)
        )
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    check_owner_or_admin(review.user_id, current_user)

    review.is_deleted = True
    await db.commit()
