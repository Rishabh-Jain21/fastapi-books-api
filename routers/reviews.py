from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_current_user, check_owner_or_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(review_id: int = Path(gt=0), db: Session = Depends(get_db)):
    review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id, models.Review.is_deleted == False)
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@router.patch("/{review_id}", response_model=schemas.ReviewResponse)
def patch_review(
    payload: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    review_id: int = Path(gt=0),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id, models.Review.is_deleted == False)
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    check_owner_or_admin(review.user_id, current_user)

    updated_data = payload.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    review = (
        db.query(models.Review)
        .filter(models.Review.id == review_id, models.Review.is_deleted == False)
        .first()
    )

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    check_owner_or_admin(review.user_id, current_user)

    review.is_deleted = True
    db.commit()
