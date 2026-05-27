# SkyCast ↔ EnRuta: Integración

## Estado Actual (Fase 0)

EnRuta usa **OpenWeatherMap directo** como fuente meteorológica primaria,
con fallback determinista basado en coordenadas. El módulo `src/weather/`
tiene una interfaz abstracta (`WeatherProvider`) lista para conectar SkyCast
cuando esté maduro.

---

## Servicios que EnRuta necesita de SkyCast (futuro)

### 1. `POST /api/v1/route-weather` ⭐ CRÍTICO

Weather a lo largo de una ruta, no solo en un punto.

**Request:**
```json
{
  "origen": {"lat": 40.4168, "lon": -3.7038},
  "destino": {"lat": 41.3874, "lon": 2.1686},
  "hora_salida": "2026-06-01T08:00:00Z",
  "num_samples": 5
}
```

**Response:**
```json
{
  "waypoints": [
    {
      "lat": 40.4168, "lon": -3.7038,
      "temperatura_c": 22.5,
      "precipitacion_mm_h": 0.0,
      "viento_kmh": 12,
      "visibilidad_km": 15,
      "alerta": "verde",
      "alerta_desc": "",
      "fuente": "skycast+owm",
      "timestamp": "2026-06-01T08:00:00Z",
      "pronostico_h": [
        {"hora": "09:00", "precip_mm_h": 0.5, "temp_c": 24},
        {"hora": "10:00", "precip_mm_h": 2.0, "temp_c": 23}
      ]
    }
  ],
  "hazard_level": "verde",
  "duration_penalty_pct": 0,
  "summary": "Sin incidencias en ruta"
}
```

---

### 2. `POST /api/v1/validate-observation` ⭐ DIFERENCIAL

Valida una observación humana contra fuentes oficiales cercanas.
Este es el *killer feature* de SkyCast para EnRuta.

**Request:**
```json
{
  "lat": 39.8628, "lon": -4.0273,
  "reporte": "helada intensa",
  "temperatura_c": -3,
  "timestamp": "2026-05-26T06:00:00Z",
  "fuente_reporte": "transportista"
}
```

**Response:**
```json
{
  "valido": true,
  "confianza": 87,
  "estaciones_cercanas": [
    {"id": 3195, "nombre": "Toledo", "distancia_km": 4.2, "temp_min": -2.5}
  ],
  "nota": "2/3 estaciones dentro de 10km confirman T < 0°C"
}
```

**¿Por qué es diferencial?** Porque convierte un "aviso de un transportista"
en un *dato validado y accionable* para el matching engine.

---

### 3. `GET /api/v1/alerts?provincia=Toledo` ⭐ URGENTE

Alertas AEMET oficiales pero servidas con estructura limpia (sin scrapear HTML).

**Response:**
```json
{
  "alerts": [
    {
      "provincia": "Toledo",
      "nivel": "naranja",
      "fenomeno": "lluvias",
      "inicio": "2026-06-01T12:00:00Z",
      "fin": "2026-06-02T06:00:00Z",
      "descripcion": "Precipitación acumulada 80mm en 12h"
    }
  ]
}
```

---

### 4. `POST /api/v1/weather-batch` (Escalabilidad)

Consulta múltiples puntos en una sola llamada (para matching batch).

**Request:**
```json
{
  "puntos": [
    {"lat": 40.4168, "lon": -3.7038},
    {"lat": 41.3874, "lon": 2.1686}
  ]
}
```

**Response:**
```json
{
  "observaciones": [
    {"lat": 40.4168, "lon": -3.7038, "temperatura_c": 22.5, ...},
    {"lat": 41.3874, "lon": 2.1686, "temperatura_c": 24.1, ...}
  ]
}
```

---

### 5. Service Account / Machine-to-Machine Auth

EnRuta necesita una API key no ligada a un humano, con:
- Rate limit alto (500 req/min para matching batch)
- Sin expiración de sesión
- Endpoint dedicado: `POST /api/v1/auth/service-account`

---

### 6. Health + Status

```json
GET /api/v1/health → {
  "status": "ok",
  "uptime_s": 3600,
  "fuentes": {
    "owm": "healthy",
    "aemet": "degraded"
  }
}
```

EnRuta consultará este endpoint antes de usar SkyCast como fuente primaria.

---

## Resumen de Prioridades para SkyCast

| # | Endpoint | Prioridad | Dependencia | Impacto en EnRuta |
|---|----------|-----------|-------------|-------------------|
| 1 | `POST /route-weather` | 🔴 Alta | Forecasting + route sampling | Matching climáticamente consciente |
| 2 | `POST /validate-observation` | 🔴 Alta | Geovalidación ya existe | 💎 **Diferencial SkyCast** |
| 3 | `GET /alerts` | 🟡 Media | AEMET data | Alertas en dashboard de EnRuta |
| 4 | `POST /weather-batch` | 🟢 Baja | Optimización | Rendimiento en matching batch |
| 5 | `POST /auth/service-account` | 🟡 Media | Auth infra | Integración automatizada |
| 6 | `GET /health` | 🟢 Baja | Monitoreo | Failover automático |

---

## EnRuta: Código de integración (ya preparado)

Cuando SkyCast tenga al menos los endpoints 1, 2 y 5:

```python
from src.weather.client import WeatherClient

# Probar conexión
w = WeatherClient("skycast", base_url="https://skycast.example.com", api_key="sk_...")
route_w = w.get_route_weather(40.4168, -3.7038, 41.3874, 2.1686)
print(f"Hazard: {route_w.hazard_level}, Penalty: {route_w.duration_penalty_pct}%")
```

No requiere cambios en `src/geo/engine.py` ni `src/matching/engine.py`
— la abstracción ya está en su lugar.
