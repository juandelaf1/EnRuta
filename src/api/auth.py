from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
from pydantic import BaseModel
from src.database import get_connection

SECRET_KEY = "enruta-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    password: str
    nombre: str
    telefono: Optional[str] = ""
    provincia_id: int = 0
    tipo: str = "transportista"  # transportista | productor | ambos


class UserOut(BaseModel):
    id: int
    email: str
    nombre: str
    tipo: str
    telefono: str
    provincia_id: int


class UserInDB(UserOut):
    password_hash: str


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_by_email(email: str) -> Optional[UserInDB]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, email, nombre, tipo, telefono, provincia_id, password_hash FROM usuarios WHERE email = ?",
        (email,)
    ).fetchone()
    if row:
        return UserInDB(**dict(row))
    return None


def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, email, nombre, tipo, telefono, provincia_id, password_hash FROM usuarios WHERE id = ?",
        (user_id,)
    ).fetchone()
    if row:
        return UserInDB(**dict(row))
    return None


def create_user(data: UserCreate) -> UserInDB:
    conn = get_connection()
    existing = conn.execute("SELECT id FROM usuarios WHERE email = ?", (data.email,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    conn.execute(
        "INSERT INTO usuarios (email, password_hash, nombre, telefono, provincia_id, tipo) VALUES (?, ?, ?, ?, ?, ?)",
        (data.email, hash_password(data.password), data.nombre, data.telefono, data.provincia_id, data.tipo)
    )
    conn.commit()
    user = get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=500, detail="Error creando usuario")
    return user


def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(token: str) -> Optional[UserInDB]:
    payload = decode_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return get_user_by_id(int(user_id))
