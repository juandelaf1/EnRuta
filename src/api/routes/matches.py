from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
import pandas as pd
from uuid import uuid4
from src.api.models import MatchResponse, MatchEvaluateRequest, MatchEvaluateResponse, MatchEvalResult
from src.api.deps import get_current_user_dep, get_logistics_evaluate_principal
from src.api.auth import UserInDB
from src.api.audit import audit_integration
from src.api.rate_limit import rate_limit
from src.database import get_connection
from src.matching.engine import match_all, compute_matches
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


def _normalize_eval_body(body: dict, request: Request):
    """Dual-read: legacy root fields OR ecosystem envelope {capability_id, payload,...}."""
    if isinstance(body, dict) and body.get("capability_id") == "logistics.evaluate_matches" and isinstance(body.get("payload"), dict):
        payload = body["payload"]
        opts = payload.get("options") or {}
        legacy = {
            "ofertas": payload.get("ofertas", []),
            "demandas": payload.get("demandas", []),
            "max_detour_pct": opts.get("max_detour_pct", 20),
            "max_detour_km": opts.get("max_detour_km", 50),
            "top_k": opts.get("top_k", 500),
        }
        correlation_id = body.get("correlation_id") or request.headers.get("X-Correlation-Id") or request.headers.get("X-Request-Id") or str(uuid4())
        contract_version = body.get("contract_version") or "logistics-l1/0.1"
        return legacy, correlation_id, contract_version, True
    correlation_id = request.headers.get("X-Correlation-Id") or request.headers.get("X-Request-Id") or (body.get("correlation_id") if isinstance(body, dict) else None) or str(uuid4())
    contract_version = (body.get("contract_version") if isinstance(body, dict) else None) or "logistics-l1/0.1"
    return body if isinstance(body, dict) else {}, correlation_id, contract_version, False


@router.post("/evaluate", response_model=MatchEvaluateResponse)
async def evaluate_matches(
    request: Request,
    principal: dict = Depends(get_logistics_evaluate_principal),
    _rl: None = Depends(rate_limit("ENRUTA_M2M_RATE_LIMIT", "120/minute")),
):
    """Evaluación stateless (sin persistir): acoplamiento Poolar L1 / uso autónomo.

    Recibe ofertas+demandas (legacy root o envelope ecosystem) y devuelve matches explicados
    (desvío, km, score, CO2 estimado, procedencia). No modifica la base de datos.
    Auth: usuario (JWT) o m2m scope logistics:evaluate (D5).
    """
    raw = await request.json()
    legacy, correlation_id, contract_version, from_envelope = _normalize_eval_body(raw, request)
    try:
        req = MatchEvaluateRequest.model_validate(legacy) if hasattr(MatchEvaluateRequest, "model_validate") else MatchEvaluateRequest.parse_obj(legacy)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    ofertas = pd.DataFrame([o.model_dump() for o in req.ofertas])
    demandas = pd.DataFrame([d.model_dump() for d in req.demandas])
    if ofertas.empty or demandas.empty:
        audit_integration(request, contract_version, "ok", {"count": 0, "correlation_id": correlation_id})
        return MatchEvaluateResponse(
            contract_version=contract_version, matches=[], count=0,
            capability_id="logistics.evaluate_matches", correlation_id=correlation_id,
            status="ok", data_status="estimated",
            provenance={"provider": "enruta", "engine": "haversine*1.3/simulacion-sobre-base-real"},
            result={"matches": [], "count": 0, "procedencia": "estimado; actores/datos pueden ser simulados segun origen"},
        )
    df = compute_matches(
        ofertas, demandas,
        max_detour_pct=req.max_detour_pct,
        max_detour_km=req.max_detour_km,
        top_k=req.top_k,
        verbose=False,
    )
    if df is None or df.empty:
        audit_integration(request, contract_version, "ok", {"count": 0, "correlation_id": correlation_id})
        return MatchEvaluateResponse(
            contract_version=contract_version, matches=[], count=0,
            capability_id="logistics.evaluate_matches", correlation_id=correlation_id,
            status="ok", data_status="estimated",
            provenance={"provider": "enruta", "engine": "haversine*1.3/simulacion-sobre-base-real"},
            result={"matches": [], "count": 0, "procedencia": "estimado; actores/datos pueden ser simulados segun origen"},
        )
    results = []
    for _, r in df.iterrows():
        results.append(MatchEvalResult(
            oferta_id=int(r["oferta_id"]),
            demanda_id=int(r["demanda_id"]),
            score=float(r["score"]),
            extra_km=float(r["extra_km"]),
            detour_pct=float(r["detour_pct"]),
            ruta_original_km=float(r.get("ruta_original_km", 0)),
            ahorro_co2_kg=float(r["ahorro_co2_kg"]),
            capacidad_usada_pct=float(r["capacidad_usada_pct"]),
            fuente=str(r.get("fuente", "")),
            ruta=str(r.get("ruta", "")),
            producto=str(r.get("producto", "")),
        ))
    audit_integration(request, contract_version, "ok", {"count": len(results), "correlation_id": correlation_id})
    resp = MatchEvaluateResponse(
        contract_version=contract_version, matches=results, count=len(results),
        capability_id="logistics.evaluate_matches", correlation_id=correlation_id,
        status="ok", data_status="estimated",
        provenance={"provider": "enruta", "engine": "haversine*1.3/simulacion-sobre-base-real"},
        result={"matches": [m.model_dump() for m in results], "count": len(results), "procedencia": "estimado; actores/datos pueden ser simulados segun origen"},
    )
    if from_envelope:
        # ensure correlation echoed in response context; headers already set by middleware if any
        pass
    return resp
