from fastapi import APIRouter, Depends, HTTPException
from src.api.auth import (
    create_user, authenticate_user, create_access_token, UserCreate,
    UserInDB
)
from src.api.models import (
    UserRegister, UserLogin, TokenResponse, UserResponse
)
from src.api.deps import get_current_user_dep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister):
    user = create_user(UserCreate(**data.model_dump()))
    token = create_access_token({"sub": str(user.id), "email": user.email, "tipo": user.tipo})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id, email=user.email, nombre=user.nombre,
            tipo=user.tipo, telefono=user.telefono, provincia_id=user.provincia_id
        )
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = create_access_token({"sub": str(user.id), "email": user.email, "tipo": user.tipo})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id, email=user.email, nombre=user.nombre,
            tipo=user.tipo, telefono=user.telefono, provincia_id=user.provincia_id
        )
    )


@router.get("/me", response_model=UserResponse)
def me(user: UserInDB = Depends(get_current_user_dep)):
    return UserResponse(
        id=user.id, email=user.email, nombre=user.nombre,
        tipo=user.tipo, telefono=user.telefono, provincia_id=user.provincia_id
    )
