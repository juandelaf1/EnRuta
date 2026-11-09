# EnRuta

**“Uber de pequeños productores rurales”**: empareja envíos de pequeños productores con repartidores/transportistas que tienen capacidad y están cerca (desvío aceptable), optimizando ruta, coste y CO₂, con ajuste por riesgo climático.

> **Producto en doble modo:** (1) **autónomo, completo y vendible por separado**; (2) **módulo logístico acoplable a [Poolar](../../Trama_Abierta/poolar/README.md)** vía contrato/API, sin duplicar la orquestación genérica de Poolar. Detalle preservado en [`docs/VISION_Y_BACKLOG.md`](docs/VISION_Y_BACKLOG.md).

## Estado actual (verificado, 2026-11-08)
*MVP de simulación/decisión — honesto, sin métricas falsas.*

- **Base geográfica real/curada:** 446 municipios con coords + población INE 2024 (`src/ingestors/municipios_data.py`), cobertura provincial. Refresco INE Tempus3 best-effort con fallback (`src/ingestors/ine.py`).
- **Actores sintéticos (simulación reproducible, seed 42):** productores, transportistas, ofertas y demandas generados en `pipeline.step3`. **No son registros reales** de MAPA/MITMA/empresas.
- **Matching:** `src/matching/engine.py` — prefiltrado Haversine + refinamiento OSRM (driving) → desvío extra/km/% y score (urgencia + aprovechamiento). Estimaciones de coste/CO₂ heurísticas (`src/pricing.py`).
- **Clima (Seam 1, verificado en vivo):** `src/weather/client.py` consume SkyCast `POST /api/v1/route-weather` (AEMET en España + fallback Open-Meteo) y aplica `adjust_route_by_weather`. Ver `docs/SKYCAST_INTEGRATION.md`.
- **Interfaces:** API FastAPI (`src/api`, auth JWT/bcrypt) y dashboard **Dash** (`src/dashboard.py`). Persistencia **SQLite** (`data/enruta.db`).
- **Limitaciones:** actores/ofertas simulados (no operativo sin datos reales/partners); OSRM público sin SLA (fallback Haversine); coste/CO₂ = estimaciones. Métricas de negocio solo con datos observados.

## Visión / backlog (objetivo, no implementado)
Backlog técnico (aplicado al producto logístico rural) — ver [`docs/VISION_Y_BACKLOG.md`](docs/VISION_Y_BACKLOG.md):
- **GeoPandas + Shapely (+ PyProj):** proximidad/cobertura real, buffers/joins espaciales (“quién está cerca”), evolución de `geo/engine.py`/H3.
- **DuckDB (+ Parquet):** capa analítica sobre rutas/matches/CO₂/KPIs (convive con SQLite).
- **UI (decisión abierta, `UI=3` por ahora — conviven):** hoy **Dash** operativo; objetivo incorporar **Streamlit** como panel analítico/operativo (opciones: migrar/reemplazar Dash, Streamlit+FastAPI, o convivir) — *pendiente de decisión*.
- **Datos/actores reales:** ingesta MAPA/MITMA/partners o carga operativa (**go/no-go** de producto operativo/vendible en modo real).
- **Contrato logístico estable y acoplamiento Poolar (L1):** ver [`docs/CONTRATO_LOGISTICO_POOLAR.md`](docs/CONTRATO_LOGISTICO_POOLAR.md).

## Relación con Poolar (sin duplicar)
- **EnRuta** = especialización logística (cercanía, ruta/desvío, capacidad, coste/CO₂, clima). **Poolar** = cooperación/orquestación genérica (personas/orgs, necesidades/capacidades, iniciativas, decisiones, auditoría).
- Poolar **delega** el cálculo logístico a EnRuta (contrato/API); EnRuta **no** reimplementa la orquestación genérica. Mismo motor, dos empaquetados: autónomo vendible + módulo acoplable.

## Stack (actual)
| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Datos/matching | pandas, SQLite (`data/enruta.db`) |
| Georrouting | Haversine + OSRM (HTTP) |
| API | FastAPI, Uvicorn, Pydantic, python-jose, bcrypt |
| Dashboard | Dash, Plotly (Streamlit en backlog) |
| Clima (seam) | SkyCast `/route-weather` (AEMET/Open-Meteo) vía `WeatherClient` |

## Uso rápido
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

python run.py pipeline   # base real + simulación (seed 42)
python run.py match      # calcular matches
python run.py api        # http://127.0.0.1:8000/docs
python run.py dashboard  # http://127.0.0.1:8050
```
> Clima vía SkyCast: `WeatherClient("skycast", base_url="http://127.0.0.1:8000/api/v1")`. Ver `docs/SKYCAST_INTEGRATION.md`.

## Estructura
```text
EnRuta/
├── run.py, requirements.txt, data/, tests/
├── docs/
│   ├── VISION_Y_BACKLOG.md          # visión preservada (fuente de verdad de intención)
│   ├── CONTRATO_LOGISTICO_POOLAR.md # acoplamiento L1 con Poolar (sin duplicar)
│   └── SKYCAST_INTEGRATION.md
└── src/
    ├── pipeline.py, database.py, pricing.py, dashboard.py
    ├── matching/engine.py
    ├── geo/engine.py
    ├── weather/client.py
    ├── api/ (main, routes: auth/ofertas/demandas/matches/weather)
    └── ingestors/ (municipios_data real curada, ine best-effort, provincias/coords)
```

## Testing
```bash
pytest tests/ -v
```

## Licencia
MIT (ver `LICENSE` si aplica en el repositorio).
