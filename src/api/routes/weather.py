from fastapi import APIRouter, Depends
from typing import List
from src.api.models import ReporteClimaticoCreate, ReporteClimaticoResponse
from src.api.deps import get_current_user_dep
from src.api.auth import UserInDB
from src.database import get_connection

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("/report", response_model=ReporteClimaticoResponse)
def reportar_clima(data: ReporteClimaticoCreate, user: UserInDB = Depends(get_current_user_dep)):
    """Un transportista reporta condiciones climáticas en su ubicación actual."""
    conn = get_connection()
    alerta = "verde"
    if data.precipitacion_mm_h and data.precipitacion_mm_h > 5:
        alerta = "amarillo"
    if data.viento_kmh and data.viento_kmh > 50:
        alerta = "naranja"
    if data.precipitacion_mm_h and data.precipitacion_mm_h > 20:
        alerta = "rojo"

    conn.execute(
        """INSERT INTO reportes_climaticos
           (usuario_id, lat, lon, temperatura_c, precipitacion_mm_h,
            viento_kmh, visibilidad_km, alerta, nota, estado)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')""",
        (user.id, data.lat, data.lon, data.temperatura_c, data.precipitacion_mm_h,
         data.viento_kmh, data.visibilidad_km, alerta, data.nota)
    )
    conn.commit()
    reporte_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM reportes_climaticos WHERE id = ?", (reporte_id,)).fetchone()
    return ReporteClimaticoResponse(**dict(row))


@router.get("/reportes", response_model=List[ReporteClimaticoResponse])
def list_reportes(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reportes_climaticos ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [ReporteClimaticoResponse(**dict(r)) for r in rows]


@router.get("/reportes/provincia/{provincia_id}", response_model=List[ReporteClimaticoResponse])
def reportes_por_provincia(provincia_id: int, limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.* FROM reportes_climaticos r
           JOIN usuarios u ON r.usuario_id = u.id
           WHERE u.provincia_id = ?
           ORDER BY r.created_at DESC LIMIT ?""",
        (provincia_id, limit)
    ).fetchall()
    return [ReporteClimaticoResponse(**dict(r)) for r in rows]
