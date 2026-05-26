import math
import requests
from typing import Optional

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos puntos (Haversine)."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def osrm_route(lat1, lon1, lat2, lon2) -> Optional[dict]:
    """Consulta OSRM para distancia real en carretera y duración."""
    try:
        url = f"{OSRM_URL}/{lon1},{lat1};{lon2},{lat2}?overview=false"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                return {
                    "distance_km": route["distance"] / 1000,
                    "duration_min": route["duration"] / 60,
                }
    except:
        pass
    return None


def distancia_optima(lat1, lon1, lat2, lon2) -> dict:
    """Distancia real (OSRM) con fallback a Haversine."""
    ruta = osrm_route(lat1, lon1, lat2, lon2)
    if ruta:
        ruta["fuente"] = "osrm"
        return ruta
    h = haversine(lat1, lon1, lat2, lon2)
    return {"distance_km": round(h, 2), "duration_min": round(h * 1.5, 1), "fuente": "haversine"}


def detour_ratio(transp_orig_lat, transp_orig_lon, transp_dest_lat, transp_dest_lon,
                 pickup_lat, pickup_lon, dropoff_lat, dropoff_lon) -> dict:
    """
    Calcula el desvío que supone para un transportista recoger y dejar mercancía.
    Devuelve km extra y % de desvío sobre ruta original.
    """
    directa = distancia_optima(transp_orig_lat, transp_orig_lon, transp_dest_lat, transp_dest_lon)
    if directa["distance_km"] == 0:
        return {"extra_km": 0, "detour_pct": 0, "ruta_directa_km": 0}

    # Ruta: origen -> pickup -> dropoff -> destino
    tramo1 = distancia_optima(transp_orig_lat, transp_orig_lon, pickup_lat, pickup_lon)
    tramo2 = distancia_optima(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
    tramo3 = distancia_optima(dropoff_lat, dropoff_lon, transp_dest_lat, transp_dest_lon)

    total_desvio = tramo1["distance_km"] + tramo2["distance_km"] + tramo3["distance_km"]
    extra = total_desvio - directa["distance_km"]

    return {
        "extra_km": round(extra, 2),
        "detour_pct": round((extra / directa["distance_km"]) * 100, 1),
        "ruta_directa_km": directa["distance_km"],
        "ruta_desvio_km": round(total_desvio, 2),
    }


def cluster_puntos(puntos, radio_km=20):
    """Agrupa puntos (lat, lon) cercanos dentro de un radio."""
    clusters = []
    usados = set()
    for i, (lat1, lon1) in enumerate(puntos):
        if i in usados:
            continue
        grupo = [(lat1, lon1)]
        usados.add(i)
        for j, (lat2, lon2) in enumerate(puntos):
            if j not in usados and haversine(lat1, lon1, lat2, lon2) <= radio_km:
                grupo.append((lat2, lon2))
                usados.add(j)
        clusters.append(grupo)
    return clusters
