from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.api.models import MatchResponse
from src.api.deps import get_current_user_dep
from src.api.auth import UserInDB
from src.database import get_connection
from src.matching.engine import match_all
from src.geo.engine import haversine
from src import pricing

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=List[MatchResponse])
def list_matches(user: UserInDB = Depends(get_current_user_dep)):
    conn = get_connection()
    rows = conn.execute(
        """SELECT m.*, o.activa as oferta_activa, d.activa as demanda_activa,
                  o.origen_lat as o_lat, o.origen_lon as o_lon,
                  o.destino_lat as d_lat, o.destino_lon as d_lon,
                  d.kg, d.origen_lat as do_lat, d.origen_lon as do_lon,
                  d.destino_lat as dd_lat, d.destino_lon as dd_lon
           FROM matches m
           JOIN ofertas o ON m.oferta_id = o.id
           JOIN demandas d ON m.demanda_id = d.id
           WHERE (o.transportista_id = ? OR d.productor_id = ?)
           ORDER BY m.id DESC LIMIT 50""",
        (user.id, user.id)
    ).fetchall()
    result = []
    for r in rows:
        rd = dict(r)
        km_ruta = haversine(rd["o_lat"], rd["o_lon"], rd["d_lat"], rd["d_lon"]) * 1.3
        extra_km = rd.get("ahorro_estimado", 0) or 0
        kg = rd.get("kg", 0) or 0
        p = pricing.calcular_ahorro(kg, km_ruta, extra_km)
        rd["coste_enruta_eur"] = p["coste_enruta_eur"]
        rd["coste_tradicional_eur"] = p["coste_tradicional_eur"]
        rd["ahorro_eur"] = p["ahorro_eur"]
        rd["ingreso_transportista_eur"] = p["ingreso_transportista_eur"]
        result.append(MatchResponse(**rd))
    return result


@router.post("/run")
def run_matching(user: UserInDB = Depends(get_current_user_dep)):
    """Ejecuta el matching engine y devuelve resumen."""
    df = match_all(top_k=500)
    if df.empty:
        return {"matches": 0, "message": "No se encontraron matches"}
    return {
        "matches": len(df),
        "mejor_score": df.iloc[0]["score"],
        "co2_total_kg": round(df["ahorro_co2_kg"].sum(), 1),
    }


@router.post("/{match_id}/accept")
def accept_match(match_id: int, user: UserInDB = Depends(get_current_user_dep)):
    conn = get_connection()
    row = conn.execute(
        """SELECT m.*, o.transportista_id, d.productor_id
           FROM matches m
           JOIN ofertas o ON m.oferta_id = o.id
           JOIN demandas d ON m.demanda_id = d.id
           WHERE m.id = ?""", (match_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Match no encontrado")
    match_dict = dict(row)
    if user.id not in (match_dict["transportista_id"], match_dict["productor_id"]):
        raise HTTPException(status_code=403, detail="No eres parte de este match")
    conn.execute("UPDATE matches SET estado = 'aceptado' WHERE id = ?", (match_id,))
    conn.commit()
    return {"status": "aceptado", "match_id": match_id}
