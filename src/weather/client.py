"""
Weather data abstraction layer for EnRuta.

Provides a unified interface for:
  - OpenWeatherMap (direct, immediate)
  - AEMET RSS alerts (official, no dependency needed)
  - SkyCast (future, when ready)

Usage:
    weather = WeatherClient.get_provider("owm")
    ruta = weather.get_route_weather(lat1, lon1, lat2, lon2)
    print(ruta.hazard_level)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
import requests
import math
import time


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PointWeather:
    lat: float
    lon: float
    temperatura_c: Optional[float] = None
    precipitacion_mm_h: Optional[float] = None
    viento_kmh: Optional[float] = None
    visibilidad_km: Optional[float] = None
    alerta: str = "verde"        # verde / amarillo / naranja / rojo
    alerta_desc: str = ""
    fuente: str = "unknown"
    timestamp: Optional[str] = None


@dataclass
class RouteWeather:
    """Weather conditions along a route, sampled at key waypoints."""
    waypoints: List[PointWeather] = field(default_factory=list)
    hazard_level: str = "verde"          # overall route hazard: aggregate of waypoints
    duration_penalty_pct: float = 0.0   # extra time % due to weather
    co2_penalty_pct: float = 0.0        # extra fuel / CO2 % due to headwind / rain
    summary: str = ""
    fuente: str = "unknown"


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------

class WeatherProvider(ABC):
    """All weather providers must implement this interface."""

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def get_point_weather(self, lat: float, lon: float) -> PointWeather:
        """Weather at a single coordinate."""
        ...

    def get_route_weather(self, lat1: float, lon1: float,
                          lat2: float, lon2: float,
                          num_samples: int = 5) -> RouteWeather:
        """Weather along a straight-line path from (lat1, lon1) to (lat2, lon2).
        Default implementation interpolates waypoints and calls get_point_weather.
        Providers may override with a more efficient batch endpoint.
        """
        waypoints = []
        for i in range(num_samples):
            frac = i / (num_samples - 1) if num_samples > 1 else 0
            lat = lat1 + (lat2 - lat1) * frac
            lon = lon1 + (lon2 - lon1) * frac
            waypoints.append(self.get_point_weather(lat, lon))

        return self._aggregate(waypoints)

    def _aggregate(self, waypoints: List[PointWeather]) -> RouteWeather:
        levels = {"verde": 0, "amarillo": 1, "naranja": 2, "rojo": 3}
        nombres = {0: "verde", 1: "amarillo", 2: "naranja", 3: "rojo"}
        max_level = 0
        rain_count = 0
        wind_count = 0

        for wp in waypoints:
            lvl = levels.get(wp.alerta, 0)
            if lvl > max_level:
                max_level = lvl
            if wp.precipitacion_mm_h and wp.precipitacion_mm_h > 2:
                rain_count += 1
            if wp.viento_kmh and wp.viento_kmh > 40:
                wind_count += 1

        # ~15% penalty if more than half the route has significant rain
        duration_penalty = 0.0
        if rain_count > len(waypoints) // 2:
            duration_penalty += 15
        if wind_count > len(waypoints) // 2:
            duration_penalty += 10
        if max_level >= 2:  # naranja
            duration_penalty += 25

        alerts = []
        if max_level >= 1:
            alerts.append(nombres[max_level])
        if rain_count > 0:
            alerts.append(f"lluvia en {rain_count}/{len(waypoints)} puntos")
        if wind_count > 0:
            alerts.append(f"viento fuerte en {wind_count}/{len(waypoints)} puntos")

        return RouteWeather(
            waypoints=waypoints,
            hazard_level=nombres[max_level],
            duration_penalty_pct=duration_penalty,
            co2_penalty_pct=duration_penalty * 0.7,  # rough correlation
            summary=" | ".join(alerts) if alerts else "Sin incidencias",
            fuente=waypoints[0].fuente if waypoints else "unknown",
        )


# ---------------------------------------------------------------------------
# OWM direct implementation (Fase 0)
# ---------------------------------------------------------------------------

class OWMProvider(WeatherProvider):
    """OpenWeatherMap direct — free API key needed."""

    def __init__(self, api_key: str = ""):
        self._api_key = api_key
        self._base = "https://api.openweathermap.org/data/2.5"

    def name(self) -> str:
        return "openweathermap"

    def get_point_weather(self, lat: float, lon: float) -> PointWeather:
        if not self._api_key:
            return self._mock(lat, lon)

        try:
            url = f"{self._base}/weather"
            r = requests.get(url, params={
                "lat": lat, "lon": lon,
                "appid": self._api_key,
                "units": "metric",
                "lang": "es",
            }, timeout=8)
            if r.status_code == 200:
                data = r.json()
                main = data.get("main", {})
                wind = data.get("wind", {})
                rain = data.get("rain", {}).get("1h", 0)
                weather = data.get("weather", [{}])[0]
                alerta = "verde"
                alerta_desc = weather.get("description", "")
                if "tormenta" in alerta_desc.lower() or "extrem" in alerta_desc.lower():
                    alerta = "rojo"
                elif "lluvia" in alerta_desc.lower() and "moderada" in alerta_desc.lower():
                    alerta = "amarillo"
                elif "lluvia intensa" in alerta_desc.lower():
                    alerta = "naranja"

                return PointWeather(
                    lat=lat, lon=lon,
                    temperatura_c=main.get("temp"),
                    precipitacion_mm_h=rain if rain else 0,
                    viento_kmh=wind.get("speed", 0) * 3.6 if wind.get("speed") else None,
                    visibilidad_km=data.get("visibility", 10000) / 1000,
                    alerta=alerta,
                    alerta_desc=alerta_desc,
                    fuente="openweathermap",
                    timestamp=str(data.get("dt", "")),
                )
        except Exception:
            pass
        return self._mock(lat, lon)

    def _mock(self, lat: float, lon: float) -> PointWeather:
        """Fallback determinista basado en coordenadas (útil para desarrollo)."""
        import hashlib
        seed = int(hashlib.md5(f"{lat:.1f}{lon:.1f}".encode()).hexdigest()[:8], 16)
        temp = 15 + (seed % 20) - 5
        rain = (seed % 30) / 10
        wind = 5 + (seed % 40)
        alerta = "verde"
        if rain > 2:
            alerta = "amarillo"
        if wind > 50:
            alerta = "naranja"
        return PointWeather(
            lat=lat, lon=lon,
            temperatura_c=temp,
            precipitacion_mm_h=rain,
            viento_kmh=wind,
            visibilidad_km=10 + (seed % 10),
            alerta=alerta,
            alerta_desc=f"Temp: {temp}°C, viento: {wind:.0f} km/h",
            fuente="owm_mock",
        )


# ---------------------------------------------------------------------------
# SkyCast stub (Fase 1/2 — preparado para cuando esté listo)
# ---------------------------------------------------------------------------

class SkyCastProvider(WeatherProvider):
    """
    Provider for SkyCast API (future).
    When SkyCast has route-weather endpoints, forecasting, and SLA,
    replace this stub with the real implementation.
    """

    def __init__(self, base_url: str = "", api_key: str = ""):
        self._base = base_url or "http://localhost:8000/api/v1"
        self._api_key = api_key

    def name(self) -> str:
        return "skycast"

    def get_point_weather(self, lat: float, lon: float) -> PointWeather:
        """Fallback a OWM hasta que SkyCast implemente point endpoint optimizado."""
        return OWMProvider().get_point_weather(lat, lon)

    def get_route_weather(self, lat1: float, lon1: float,
                          lat2: float, lon2: float,
                          num_samples: int = 5) -> RouteWeather:
        """
        Intentar llamar al endpoint de ruta de SkyCast.
        Si falla, degradar a OWM + interpolación.
        """
        try:
            url = f"{self._base}/route-weather"
            r = requests.post(url, json={
                "origen_lat": lat1, "origen_lon": lon1,
                "destino_lat": lat2, "destino_lon": lon2,
                "num_samples": num_samples,
            }, headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }, timeout=10)
            if r.status_code == 200:
                data = r.json()
                waypoints = [PointWeather(**w) for w in data.get("waypoints", [])]
                if waypoints:
                    return self._aggregate(waypoints)
        except Exception:
            pass

        # Degradación elegante
        return OWMProvider().get_route_weather(lat1, lon1, lat2, lon2, num_samples)


# ---------------------------------------------------------------------------
# Factory + alert helpers
# ---------------------------------------------------------------------------

class WeatherClient:
    """Entry point for all weather queries from EnRuta."""

    _providers = {
        "owm": OWMProvider,
        "skycast": SkyCastProvider,
    }

    def __init__(self, provider_name: str = "owm", **kwargs):
        cls = self._providers.get(provider_name, OWMProvider)
        self._provider = cls(**kwargs)

    def get_point_weather(self, lat, lon) -> PointWeather:
        return self._provider.get_point_weather(lat, lon)

    def get_route_weather(self, lat1, lon1, lat2, lon2, num_samples=5) -> RouteWeather:
        return self._provider.get_route_weather(lat1, lon1, lat2, lon2, num_samples)

    @classmethod
    def get_provider(cls, name: str = "owm", **kwargs) -> WeatherProvider:
        return cls._providers.get(name, OWMProvider)(**kwargs)


def adjust_route_by_weather(route_data: dict, weather: RouteWeather) -> dict:
    """
    Enrich a route dict with weather-adjusted values.
    Use in: src/geo/engine.py → distancia_optima()
    """
    if weather.hazard_level == "rojo":
        route_data["recommendation"] = "cancel"  # too dangerous
    elif weather.hazard_level == "naranja":
        route_data["recommendation"] = "caution"
    elif weather.hazard_level == "amarillo":
        route_data["recommendation"] = "check_conditions"

    penalty = weather.duration_penalty_pct / 100
    route_data["duration_min"] = round(route_data["duration_min"] * (1 + penalty), 1)
    route_data["weather"] = weather.summary
    route_data["weather_hazard"] = weather.hazard_level
    route_data["weather_fuente"] = weather.fuente
    return route_data
