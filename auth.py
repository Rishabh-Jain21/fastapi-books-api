from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from config import settings
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from schemas import CurrentUser

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth_bearer = OAuth2PasswordBearer(tokenUrl="/users/token")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_minutes: int,
):
    encode = {"sub": username, "user_id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    encode.update({"exp": expires})
    return jwt.encode(
        claims=encode,
        key=settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def get_current_user(token: str = Depends(oauth_bearer)) -> Optional[CurrentUser]:
    try:
        payload = jwt.decode(token, key=settings.secret_key.get_secret_value())
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("user_id")
        user_role: str = payload.get("role", "")
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate Credentials",
            )
        return CurrentUser(username=username, user_id=user_id, role=user_role)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Credentials",
        )


def require_role(*roles: str):
    def checker(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        return current_user

    return checker


def check_owner_or_admin(resource_user_id: int, current_user: CurrentUser):
    if resource_user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
