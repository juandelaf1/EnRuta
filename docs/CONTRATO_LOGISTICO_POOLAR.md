# Contrato logístico EnRuta ↔ Poolar (L1, acoplamiento sin duplicar)

> Objetivo: que EnRuta funcione como **producto autónomo vendible** y, a la vez, como **módulo logístico acoplable a Poolar**, sin que Poolar reimplemente logística ni EnRuta duplique la orquestación genérica de Poolar.

## 1. Límites (quién hace qué)
| Responsabilidad | EnRuta (logística especializada) | Poolar (cooperación/orquestación) |
|---|---|---|
| Identidad, orgs, personas | No (salvo auth propia en modo autónomo) | Sí |
| Necesidades/capacidades/recursos genéricos, problemas, iniciativas, decisiones, auditoría | No | Sí |
| Matching por desvío/ruta, capacidad (kg), urgencia, coste/CO₂, clima en ruta | **Sí (núcleo)** | No (delega) |
| Georrouting (OSRM/Haversine) y proximidad/geo | **Sí** | Consume resultado |
| Validación/ajuste climático de ruta | **Sí** (vía SkyCast) | Puede registrar evidencia/decisión |

## 2. Mapeo conceptual (Poolar → EnRuta)
| Concepto Poolar | Concepto EnRuta | Notas |
|---|---|---|
| Necesidad (transporte de mercancía, origen→destino, kg, producto, urgencia, ventana) | **Demanda** (`DemandaCreate/Response`: origen/destino lat/lon/localidad, `kg`, `producto`, `urgente`, `fecha/ventana`) | Poolar expresa la necesidad; EnRuta calcula viabilidad/match. |
| Capacidad (ruta con capacidad disponible, vehículo, horario) | **Oferta** (`OfertaCreate/Response`: origen/destino, `capacidad_disponible_kg`, `fecha`, `precio_sugerido`) | Capacidad de ruta, no capacidad genérica. |
| Resultado de matching / opción para decidir | **Match** (`MatchResponse`: `oferta_id, demanda_id, score, estado, ahorro_estimado, co2_evitado_kg` + costes/ingreso calculados) | Poolar lo usa como alternativa/evidencia para una `Decision/Iniciativa`. |
| Evidencia/riesgo climático | Ajuste de ruta (`weather_hazard/recommendation/penalty`) + validación de observación | Se adjunta como procedencia/evidencia. |

## 3. Contrato de integración (objetivo, estable) — L1 API
EnRuta ya expone (modo autónomo, ver `src/api`, OpenAPI en `/docs` y `/openapi.json`): `POST /auth/*`, `POST/GET /ofertas`, `POST/GET /demandas`, `GET /matches`, `POST /matches/run`, `POST /matches/{id}/accept`, **`POST /matches/evaluate` (stateless, L1)**, rutas `weather/*`, `GET /health`, `GET /provincias`. Procedencia: ver `../../docs/PROVENANCE_CONVENTION.md` (P1).

Para acoplamiento con Poolar, estandarizar/estabilizar estas capacidades (compatibles hacia atrás con lo actual):

### 3.1 Calcular matches logísticos (núcleo delegable)
- **Persistido (autónomo):** `POST /matches/run` (ejecuta `match_all(top_k=500)`, auth usuario) → resumen `{matches, mejor_score, co2_total_kg}`; `GET /matches` lista matches persistidos.
- **Stateless (L1, implementado):** `POST /matches/evaluate` (`MatchEvaluateRequest` → `MatchEvaluateResponse`, `contract_version="logistics-l1/0.1"`). Acepta lotes de **demandas+ofertas** + opciones (`max_detour_pct|km`, `top_k`) y devuelve matches explicados **sin persistir**: `oferta_id, demanda_id, score, extra_km, detour_pct, ruta_original_km, ahorro_co2_kg, capacidad_usada_pct, fuente, ruta, producto, procedencia`. Núcleo: `src/matching/engine.compute_matches` (puro) + `geo/pricing`.
- **Pendiente L1:** enriquecer con coste/ahorro desglosado y `recomendacion_clima/hazard` por match cuando se integre clima en evaluación; `contract_version`/`capabilities` en `/health`; auth m2m (D5).

### 3.2 Clima en ruta (ya integrable)
- EnRuta consume SkyCast (`/api/v1/route-weather`); internamente `WeatherClient.get_route_weather` → `adjust_route_by_weather` (recomendación/penalización). Exponer/confirmar un endpoint de **riesgo climático por ruta** con el mismo shape (`hazard_level, duration_penalty_pct, summary, fuente, waypoints`) para que Poolar pueda adjuntarlo como evidencia.

### 3.3 Salud y metadatos
- `GET /health` → `{status, version, service}`. Añadir (futuro) `capabilities`/`contract_version` y procedencia de datos (p.ej. `actores: simulados|reales`, fuente base municipal).

## 4. Propiedades del contrato
- **Idempotencia:** la evaluación de matching sobre la misma entrada + opciones produce el mismo resultado (matching determinista dado el motor; OSRM/clima son dependencias externas — declarar `fuente/fecha`).
- **Procedencia:** marcar estimaciones (coste/CO₂) y origen de datos (simulado vs real). No presentar estimaciones como observadas.
- **Errores:** `4xx` validación, `503` dependencia externa (OSRM/SkyCast) con degradación documentada (fallback Haversine/mock) cuando aplique.
- **Versionado:** `contract_version` semántico; cambios incompatibles = versión mayor.
- **Autonomía:** el contrato no exige a Poolar; EnRuta sigue operable standalone (auth/almacenamiento propios).

## 5. Autenticación / modos
- **Autónomo:** auth propia (JWT, usuarios EnRuta) como hoy.
- **Acoplado a Poolar (objetivo):** confianza servicio-a-servicio (API key / m2m token, o red interna) + `caller`/`correlation_id` para auditoría; autorización fina delegada a Poolar cuando actúa como orquestador. (Alinear con SkyCast service-account previsto en `SKYCAST_INTEGRATION.md`).

## 6. Pasos de implementación (incrementales)
1. **P2-doc (hecho):** fijar contrato y mapeo. 
2. **Hecho (2026-11-08/09):** `POST /matches/evaluate` **stateless** (demandas+ofertas → matches explicados, `contract_version`, `procedencia`) reutilizando `compute_matches`/`geo/pricing`, sin romper `/matches/run`. SkyCast `route-weather` añade `contract_version`/`procedencia` (backward-compatible).
3. Normalizar respuesta explicada (detour, costes, clima por match, procedencia/fuentes unificada) — parcial.
4. Añadir `contract_version`/`capabilities` a `/health` (EnRuta, SkyCast).
5. Definir adaptador en Poolar (dominio `logistics`) que traduzca necesidad/capacidad ↔ demanda/oferta y consuma (2)-(4). **Sin duplicar** el motor.

*Estado: L1 en progreso (pasos 1-2 parciales hechos, 2026-11-09).*