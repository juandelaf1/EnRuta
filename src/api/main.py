from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, ofertas, demandas, matches, weather
from src.database import init_db, get_connection
from src.api.models import ProvinciaResponse

app = FastAPI(
    title="EnRuta API",
    description="Logística colaborativa rural + inteligencia climática",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ofertas.router)
app.include_router(demandas.router)
app.include_router(matches.router)
app.include_router(weather.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0", "service": "enruta-api"}


@app.get("/provincias", response_model=list[ProvinciaResponse])
def list_provincias():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM provincias ORDER BY nombre").fetchall()
    return [ProvinciaResponse(**dict(r)) for r in rows]
