from fastapi import Header, HTTPException, Request, status
from src.api.auth import get_current_user, UserInDB
from src.api.m2m import M2MCaller, verify_m2m


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


async def get_logistics_evaluate_principal(
    request: Request,
    authorization: str = Header("", alias="Authorization"),
    x_api_key: str = Header("", alias="X-API-Key"),
) -> dict:
    """Acepta usuario (JWT) o m2m con scope logistics:evaluate (D5)."""
    candidate = (x_api_key or "").strip()
    if not candidate and authorization.startswith("Bearer "):
        candidate = authorization.replace("Bearer ", "", 1).strip()
    # intenta m2m primero
    try:
        m2m = verify_m2m(candidate, required_scope="logistics:evaluate")
    except HTTPException:
        raise
    if m2m is not None:
        request.state.caller = m2m.caller
        return {"type": "m2m", "caller": m2m.caller}
    # fallback: usuario
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.replace("Bearer ", "", 1).strip()
    user = get_current_user(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    request.state.caller = f"user:{user.id}"
    return {"type": "user", "user_id": user.id}
