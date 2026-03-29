from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/{review_id}", response_model=schemas.ReviewResponse)
def get_review(review_id: int = Path(gt=0), db: Session = Depends(get_db)):
    review = db.get(models.Review, review_id)

    if not review or review.is_deleted == True:
        raise HTTPException(status_code=404, detail="Review not found")

    return review


@router.patch("/{review_id}", response_model=schemas.ReviewResponse)
def patch_review(
    payload: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    review_id: int = Path(gt=0),
    current_user: schemas.CurrentUser = Depends(get_current_user),
):
    review = db.get(models.Review, review_id)

    if not review or review.is_deleted == True:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )

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
    review = db.get(models.Review, review_id)

    if not review or review.is_deleted == True:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )

    review.is_deleted = True
    db.commit()
