# EnRuta — Visión y backlog (documento de preservación)

> Propósito: **preservar la perspectiva original** de lo que se quería lograr con EnRuta, junto con el estado verificado y el backlog técnico. Este documento no se sobreescribe con cambios tácticos; se actualiza añadiendo contexto/fechas.

## Visión de producto (núcleo, estable)
**“Uber de pequeños productores rurales”.** Emparejar envíos de pequeños productores con repartidores/transportistas que tengan capacidad y estén cerca (o con desvío aceptable), reduciendo coste, ineficiencia y CO₂, y facilitando la distribución rural.

Formulación histórica (README 866c232/0812e0c, producto auténtico): *“Collaborative Rural Logistics Platform — conectar productores rurales con transportistas que tienen capacidad disponible en sus rutas. Reducir costes, desperdicio alimentario y emisiones de CO₂.”* Matching con scoring geoespacial (OSRM + Haversine), por desvío/capacidad/urgencia.

> Nota histórica: el commit `8abc55a` (“Analytics Engineering experiment / transporte público”, DuckDB/GeoPandas/Streamlit) reencuadró mal el *producto*, pero reflejaba un **backlog de herramientas** que se quieren adoptar. La visión de producto correcta es la logística rural colaborativa (arriba), no transporte público.

## Estado actual verificado (2026-11-08)
- Pipeline: base municipal **real/curada** (446 municipios, coords + población INE 2024, `ingestors/municipios_data.py`); refresco INE best-effort con fallback (`ingestors/ine.py`). **Actores/ofertas/demandas sintéticos (seed 42)** en `pipeline.step3`, etiquetados como simulación — *no* son registros reales MAPA/MITMA.
- Matching: `matching/engine.py` (prefiltro Haversine + OSRM driving) → desvío/score; pricing/CO₂ heurísticos (`pricing.py`).
- Clima (Seam 1, verificado en vivo): `weather/client.py` consume SkyCast `/route-weather` (AEMET en España + fallback Open-Meteo), ajuste por riesgo; `validate-observation` operativo en SkyCast.
- Interfaces: API FastAPI (`src/api`) + dashboard Dash (`src/dashboard.py`), SQLite `data/enruta.db`. OSRM público sin SLA.

## Backlog/objetivo técnico (herramientas deseadas, no implementadas)
Estas herramientas se quieren usar para hacer el producto real/analítico (aplicadas al *producto logístico rural*, no a transporte público):
- **GeoPandas + Shapely (+ PyProj)**: proximidad/cobertura real, buffers, joins espaciales productor↔repartidor; mejorar/sustituir clustering Haversine y preparar H3.
- **DuckDB (+ Parquet)**: capa analítica sobre rutas/matches/CO₂/KPIs (convive con SQLite transaccional).
- **Streamlit**: decisión pendiente (reemplaza Dash, o Streamlit+FastAPI, o conviven) como panel analítico/operativo.
- **Datos reales**: evolución desde actores sintéticos a actores/ofertas reales (MAPA/MITMA/partners/carga operativa) — *go/no-go* de producto operativo.
- **H3**: clustering/indexación compatible con ecosistema (SkyCast/GeoRisk/Anexo) donde tenga sentido.

## Relación con Poolar/Trama Abierta (principio de producto, no duplicar)
Poolar/Trama Abierta es “infraestructura abierta de cooperación” (necesidades/capacidades/recursos/matching, decisiones, auditoría). **No construir dos productos iguales.**

**Requisito estratégico:** EnRuta debe funcionar en **doble modo**:
1. **Producto autónomo completo, vendible por separado**: resuelve de punta a punta el matching logístico rural (“Uber de pequeños productores rurales”) con su propia operación/datos/valor.
2. **Módulo acoplable a Poolar**: expone el **dominio logístico rural** (emparejamiento envíos/capacidad, routing/desvío, coste/CO₂, clima) como capacidad consumible por Poolar vía **contratos/API/puertos** (p.ej. dominio `logistics`; delegación tipo `Matching/Geo/Optimization`), sin que Poolar reimplemente la logística ni EnRuta duplique la orquestación genérica de Poolar.

Implicación: mantener límites claros (EnRuta = especialización logística; Poolar = cooperación/orquestación genérica) y un contrato de integración estable, preservando la autonomía comercial/operativa de EnRuta.

## Documentos relacionados
- `docs/SKYCAST_INTEGRATION.md` (seam clima)
- `../../PLAN_IMPLEMENTACION_ENRUTA.md`, `../../PROJECT_RADAR.md` (raíz workspace)
- README histórico: `git show 866c232:README.md` (producto auténtico)
- Commits: `8abc55a` (reencuadre erróneo de producto, tooling deseado)
