from passlib.context import CryptContext
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta, UTC
from pydantic import EmailStr

from app.config import settings
from app.dbcrud import UserCRUD

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=180)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    user = await UserCRUD.find_one_or_none(email=email)
    if not user and verify_password(password, user.password):
        return None
    return user
