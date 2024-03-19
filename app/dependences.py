from fastapi import Request, HTTPException, Depends, status
from jwt import decode, PyJWTError
from datetime import datetime, UTC

from app.config import settings
from app.dbcrud import UserCRUD


def get_token(request: Request):
    token = request.cookies.get('ref_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="There is no active user session")
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unhandled exception")
    expire: str = payload.get('exp')
    if not expire or (int(expire) < datetime.now(UTC).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unrecognized user")
    user = await UserCRUD.find_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No user found")
    return user


user = get_current_user()
