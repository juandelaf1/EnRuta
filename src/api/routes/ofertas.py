from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.api.models import OfertaCreate, OfertaResponse
from src.api.deps import get_current_user_dep
from src.api.auth import UserInDB
from src.database import get_connection
from src.geo.engine import haversine
from src import pricing

router = APIRouter(prefix="/ofertas", tags=["ofertas"])


@router.get("", response_model=List[OfertaResponse])
def list_ofertas(activas: bool = True):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ofertas WHERE activa = ? ORDER BY id DESC LIMIT 100",
        (1 if activas else 0,)
    ).fetchall()
    return [OfertaResponse(**dict(r)) for r in rows]


@router.post("", response_model=OfertaResponse)
def create_oferta(data: OfertaCreate, user: UserInDB = Depends(get_current_user_dep)):
    if user.tipo not in ("transportista", "ambos"):
        raise HTTPException(status_code=403, detail="Solo transportistas pueden crear ofertas")
    km_aprox = haversine(data.origen_lat, data.origen_lon, data.destino_lat, data.destino_lon) * 1.3
    if data.precio_sugerido <= 0:
        data.precio_sugerido = pricing.precio_sugerido_oferta(data.capacidad_disponible_kg, km_aprox)
    ingreso = pricing.ingreso_transportista(0, data.capacidad_disponible_kg)
    conn = get_connection()
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM ofertas").fetchone()[0]
    conn.execute(
        """INSERT INTO ofertas
           (id, transportista_id, origen_localidad, origen_lat, origen_lon,
            destino_localidad, destino_lat, destino_lon, fecha,
            capacidad_disponible_kg, precio_sugerido, activa)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (next_id, user.id, data.origen_localidad, data.origen_lat, data.origen_lon,
         data.destino_localidad, data.destino_lat, data.destino_lon,
         data.fecha, data.capacidad_disponible_kg, data.precio_sugerido)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM ofertas WHERE id = ?", (next_id,)).fetchone()
    resp = dict(row)
    resp["ingreso_estimado_eur"] = ingreso["total_eur"]
    return OfertaResponse(**resp)


@router.get("/{oferta_id}", response_model=OfertaResponse)
def get_oferta(oferta_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM ofertas WHERE id = ?", (oferta_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return OfertaResponse(**dict(row))
