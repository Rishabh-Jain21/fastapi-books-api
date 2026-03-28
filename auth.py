from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from config import settings
from jose import jwt

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str, user_id: int, expires_minutes: int):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    encode.update({"exp": expires})
    return jwt.encode(
        claims=encode,
        key=settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
