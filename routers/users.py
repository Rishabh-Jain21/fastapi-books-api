from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from auth import create_access_token, hash_password, verify_password
from config import settings
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.CreateUserRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).filter(
            (models.User.username == user.username) | (models.User.email == user.email)
        )
    )
    existing_user = result.scalar_one_or_none()

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
    await db.commit()

    return create_user_model


@router.post("/token", response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(
        select(models.User).filter(models.User.username == form_data.username)
    )

    user = result.scalar_one_or_none()

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
