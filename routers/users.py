from fastapi import APIRouter, Depends
import schemas
import models
from database import get_db
from sqlalchemy.orm import Session
from auth import hash_password, verify_password


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/")
def create_user(user: schemas.CreateUserRequest, db: Session = Depends(get_db)):
    create_user_model = models.User(
        email=user.email,
        username=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        is_active=True,
    )

    return create_user_model
