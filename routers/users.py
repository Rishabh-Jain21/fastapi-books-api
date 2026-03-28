from fastapi import APIRouter, Depends, status, HTTPException
import schemas
import models
from database import get_db
from sqlalchemy.orm import Session
from auth import hash_password, verify_password


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.CreateUserRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User)
        .filter(
            (models.User.username == user.username) | (models.User.email == user.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    create_user_model = models.User(
        email=user.email,
        username=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()

    return create_user_model
