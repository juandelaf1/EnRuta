from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.api.models import DemandaCreate, DemandaResponse
from src.api.deps import get_current_user_dep
from src.api.auth import UserInDB
from src.database import get_connection
from src.geo.engine import haversine
from src import pricing

router = APIRouter(prefix="/demandas", tags=["demandas"])


@router.get("", response_model=List[DemandaResponse])
def list_demandas(activas: bool = True):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM demandas WHERE activa = ? ORDER BY urgente DESC, id DESC LIMIT 100",
        (1 if activas else 0,)
    ).fetchall()
    return [DemandaResponse(**dict(r)) for r in rows]


@router.post("", response_model=DemandaResponse)
def create_demanda(data: DemandaCreate, user: UserInDB = Depends(get_current_user_dep)):
    if user.tipo not in ("productor", "ambos"):
        raise HTTPException(status_code=403, detail="Solo productores pueden crear demandas")
    km_aprox = haversine(data.origen_lat, data.origen_lon, data.destino_lat, data.destino_lon) * 1.3
    coste = pricing.coste_estimado_demanda(data.kg, km_aprox)
    conn = get_connection()
    next_id = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM demandas").fetchone()[0]
    conn.execute(
        """INSERT INTO demandas
           (id, productor_id, origen_localidad, origen_lat, origen_lon,
            destino_localidad, destino_lat, destino_lon, kg, producto, urgente, activa)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (next_id, user.id, data.origen_localidad, data.origen_lat, data.origen_lon,
         data.destino_localidad, data.destino_lat, data.destino_lon,
         data.kg, data.producto, data.urgente)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM demandas WHERE id = ?", (next_id,)).fetchone()
    resp = dict(row)
    resp["coste_enruta_eur"] = coste["coste_enruta_eur"]
    resp["coste_tradicional_eur"] = coste["coste_tradicional_eur"]
    resp["ahorro_eur"] = coste["ahorro_eur"]
    return DemandaResponse(**resp)


@router.get("/{demanda_id}", response_model=DemandaResponse)
def get_demanda(demanda_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM demandas WHERE id = ?", (demanda_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Demanda no encontrada")
    return DemandaResponse(**dict(row))
