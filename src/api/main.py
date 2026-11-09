import os
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, ofertas, demandas, matches, weather
from src.database import init_db, get_connection
from src.api.models import ProvinciaResponse

app = FastAPI(
    title="EnRuta API",
    description="Logística colaborativa rural + inteligencia climática",
    version="0.1.0",
)

_cors_origins = [o.strip() for o in os.getenv("ENRUTA_CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,  # Bearer/API key auth; no cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    cid = request.headers.get("X-Correlation-Id") or request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.correlation_id = cid
    response = await call_next(request)
    response.headers["X-Correlation-Id"] = cid
    return response

app.include_router(auth.router)
app.include_router(ofertas.router)
app.include_router(demandas.router)
app.include_router(matches.router)
app.include_router(weather.router)


@app.on_event("startup")
def startup():
    init_db()
    if os.getenv("ENRUTA_SECRET_KEY", "") in ("", "enruta-secret-change-in-production") and os.getenv("ENRUTA_ENV", "").lower() != "test":
        import logging
        logging.getLogger(__name__).warning(
            "ENRUTA_SECRET_KEY usa valor por defecto/dev o no está configurada; configurar secreto fuerte en producción (P7/seguridad)."
        )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.1.0",
        "service": "enruta-api",
        "contract_version": "logistics-l1/0.1",
        "capabilities": {
            "matches_evaluate_stateless": True,
            "matches_run_persisted": True,
            "weather_route_via_skycast": True,
            "openapi": "/openapi.json",
        },
    }


@app.get("/ready")
def ready():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        return {"ready": True, "database": "connected", "service": "enruta-api"}
    except Exception as exc:
        return {"ready": False, "database": "unavailable", "detail": str(exc)}


@app.get("/provincias", response_model=list[ProvinciaResponse])
def list_provincias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM provincias ORDER BY nombre").fetchall()
    return [ProvinciaResponse(**dict(r)) for r in rows]
