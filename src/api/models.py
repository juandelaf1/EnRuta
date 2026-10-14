from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Usuarios ---
class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=6)
    nombre: str
    telefono: Optional[str] = ""
    provincia_id: int = 0
    tipo: str = "transportista"  # transportista | productor | ambos


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    nombre: str
    tipo: str
    telefono: str
    provincia_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Ofertas ---
class OfertaCreate(BaseModel):
    origen_localidad: str
    origen_lat: float
    origen_lon: float
    destino_localidad: str
    destino_lat: float
    destino_lon: float
    fecha: str = ""
    capacidad_disponible_kg: float
    precio_sugerido: float = 0


class OfertaResponse(BaseModel):
    id: int
    transportista_id: int
    origen_localidad: str
    origen_lat: float
    origen_lon: float
    destino_localidad: str
    destino_lat: float
    destino_lon: float
    fecha: str
    capacidad_disponible_kg: float
    precio_sugerido: float
    activa: int
    ingreso_estimado_eur: Optional[float] = None


# --- Demandas ---
class DemandaCreate(BaseModel):
    origen_localidad: str
    origen_lat: float
    origen_lon: float
    destino_localidad: str
    destino_lat: float
    destino_lon: float
    kg: float
    producto: str
    urgente: int = 0


class DemandaResponse(BaseModel):
    id: int
    productor_id: int
    origen_localidad: str
    origen_lat: float
    origen_lon: float
    destino_localidad: str
    destino_lat: float
    destino_lon: float
    kg: float
    producto: str
    urgente: int
    activa: int
    coste_enruta_eur: Optional[float] = None
    coste_tradicional_eur: Optional[float] = None
    ahorro_eur: Optional[float] = None


# --- Matches ---
class MatchResponse(BaseModel):
    id: int
    oferta_id: int
    demanda_id: int
    ahorro_estimado: float
    co2_evitado_kg: float
    score: Optional[float] = 0
    estado: str = "pendiente"
    coste_enruta_eur: Optional[float] = None
    coste_tradicional_eur: Optional[float] = None
    ahorro_eur: Optional[float] = None
    ingreso_transportista_eur: Optional[float] = None


class MatchAccept(BaseModel):
    match_id: int


# --- Reportes climáticos ---
class ReporteClimaticoCreate(BaseModel):
    lat: float
    lon: float
    temperatura_c: Optional[float] = None
    precipitacion_mm_h: Optional[float] = None
    viento_kmh: Optional[float] = None
    visibilidad_km: Optional[float] = None
    nota: str = ""


class ReporteClimaticoResponse(BaseModel):
    id: int
    usuario_id: int
    lat: float
    lon: float
    temperatura_c: Optional[float]
    precipitacion_mm_h: Optional[float]
    viento_kmh: Optional[float]
    alerta: str
    estado: str
    nota: str


# --- Provincias ---
class ProvinciaResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    comunidad: str
