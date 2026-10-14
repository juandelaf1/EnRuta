from fastapi import Header, HTTPException, status
from src.api.auth import get_current_user, UserInDB


async def get_current_user_dep(authorization: str = Header(...)) -> UserInDB:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.replace("Bearer ", "")
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


async def get_optional_user(authorization: str = Header("")) -> UserInDB | None:
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    return get_current_user(token)
