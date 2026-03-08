from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{review_id}")
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.get(models.Review, review_id)

    if not review or review.is_deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.patch("/{review_id}")
def patch_review(
    review_id: int, payload: schemas.ReviewUpdate, db: Session = Depends(get_db)
):
    review = db.get(models.Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    updated_data = payload.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.get(models.Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.is_deleted = True
    db.commit()
