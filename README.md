# EnRuta — Logística Colaborativa Rural

Plataforma que conecta productores rurales con transportistas que tienen espacio disponible en sus rutas. Reduce costes, desperdicio alimentario y emisiones de CO₂.

## Stack

- **Dashboard**: Dash + Plotly (mapa OpenStreetMap)
- **Geo**: OSRM (routing) + Haversine (fallback)
- **Datos**: Dataset estático de 360 municipios españoles (tech debt: API INE + OSM Overpass pendiente)
- **Matching**: Algoritmo greedy con score por desvío, capacidad y urgencia

## Quickstart

```bash
pip install -r requirements.txt
python src/pipeline.py   # Carga datos sintéticos
python src/matching/engine.py  # Calcula matches
python src/dashboard.py  # Abre http://localhost:8050
```

## Estructura

```
src/
  pipeline.py          # Ingesta de datos
  database.py          # SQLite + modelos
  dashboard.py         # Dash web app
  ingestors/
    provincias.py      # 52 provincias españolas
    municipios_data.py # 360 municipios con coordenadas
    poblacion.py       # Población por provincia
  geo/
    engine.py          # OSRM + Haversine + detour
  matching/
    engine.py          # Match offers-demandas
```

## Tech Debt

- [ ] Sustituir dataset estático de municipios por API INE real + OSM Overpass
- [ ] Sustituir datos sintéticos de productores/transportistas por MAPA real + MITMA
- [ ] Self-host OSRM con Spain extract en Docker
- [ ] PostGIS en lugar de SQLite
- [ ] Autenticación, registro de usuarios, perfiles
- [ ] Notificaciones en tiempo real

## Resultados actuales

| Métrica | Valor |
|---------|-------|
| Municipios | 360 |
| Población cubierta | 29.9M |
| Productores sintéticos | 1,007 |
| Transportistas sintéticos | 353 |
| Ofertas activas | ~550 |
| Demandas activas | ~530 |
| Matches encontrados | 335 |
| CO₂ ahorro total | 3,566 kg |
