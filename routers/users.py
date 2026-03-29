from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import schemas
import models
from database import get_db
from sqlalchemy.orm import Session
from auth import hash_password, verify_password, create_access_token
from config import settings

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
        username=user.username,
        password_hash=hash_password(user.password),
        is_active=True,
    )

    db.add(create_user_model)
    db.commit()

    return create_user_model


@router.post("/token", response_model=schemas.Token, status_code=status.HTTP_200_OK)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(
        user.username,
        user_id=user.id,
        role=user.role,
        expires_minutes=settings.access_token_expire_minutes,
    )

    return schemas.Token(access_token=token, token_type="bearer")
