"""Proximidad/cobertura geoespacial (GeoPandas + Shapely).

Aporta valor al producto ("quién está cerca / con capacidad al alcance"): buffers,
búsqueda por radio y cobertura productor↔repartidor, usando CRS métrico para distancias.
Mantiene compatibilidad: si faltan deps, los llamadores pueden usar el fallback Haversine
en `geo.engine`.
"""

from __future__ import annotations

from typing import Any

try:
    import geopandas as gpd
    from shapely.geometry import Point
    GEOPANDAS_AVAILABLE = True
except Exception:  # pragma: no cover
    gpd = None  # type: ignore
    Point = None  # type: ignore
    GEOPANDAS_AVAILABLE = False

# WGS84 para entrada/salida; Web Mercator métrico para buffers/distancias (suficiente MVP España).
CRS_WGS84 = "EPSG:4326"
CRS_METRIC = "EPSG:3857"


def _require_geopandas() -> None:
    if not GEOPANDAS_AVAILABLE:
        raise RuntimeError("GeoPandas/Shapely no disponibles; instala geopandas, shapely, pyproj.")


def points_gdf(records: list[dict[str, Any]], lat: str = "lat", lon: str = "lon") -> "gpd.GeoDataFrame":
    """Crea un GeoDataFrame en WGS84 a partir de dicts con lat/lon."""
    _require_geopandas()
    if not records:
        return gpd.GeoDataFrame(records, geometry=[], crs=CRS_WGS84)
    geom = [Point(float(r[lon]), float(r[lat])) for r in records]
    return gpd.GeoDataFrame(records, geometry=geom, crs=CRS_WGS84)


def nearby(
    origin_lat: float,
    origin_lon: float,
    candidates: list[dict[str, Any]],
    radius_km: float,
    lat: str = "lat",
    lon: str = "lon",
) -> list[dict[str, Any]]:
    """Devuelve candidatos dentro de `radius_km` del origen (distancia en buffer métrico).

    Añade `_distance_km` aproximada (en el CRS métrico). Si no hay geopandas, lanza
    RuntimeError (el llamador debe hacer fallback a Haversine).
    """
    _require_geopandas()
    if not candidates or radius_km <= 0:
        return []
    cand = points_gdf(candidates, lat=lat, lon=lon).to_crs(CRS_METRIC)
    origin = gpd.GeoDataFrame(
        [{"_origin": 1}],
        geometry=[Point(float(origin_lon), float(origin_lat))],
        crs=CRS_WGS84,
    ).to_crs(CRS_METRIC)
    origin_geom = origin.geometry.iloc[0]
    # filtro por buffer (cobertura) + distancia
    buffered = origin_geom.buffer(radius_km * 1000.0)
    within = cand[cand.geometry.within(buffered)].copy()
    if within.empty:
        return []
    within["_distance_km"] = (within.geometry.distance(origin_geom) / 1000.0).round(3)
    # soltar geometría para devolver dicts planos
    cols = [c for c in within.columns if c != "geometry"]
    return within[cols].to_dict(orient="records")


def coverage_summary(
    origins: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    radius_km: float,
    origin_lat: str = "lat",
    origin_lon: str = "lon",
    target_lat: str = "lat",
    target_lon: str = "lon",
) -> dict[str, Any]:
    """Resumen de cobertura: cuántos orígenes tienen >=1 objetivo a `radius_km`.

    Útil para “productor con repartidor cerca”. Devuelve conteos y ratio (sin métricas falsas
    sobre demanda real; es una medida geométrica sobre el conjunto dado).
    """
    _require_geopandas()
    if not origins or not targets or radius_km <= 0:
        return {"origins": len(origins), "targets": len(targets), "covered": 0, "coverage_ratio": 0.0, "radius_km": radius_km}
    tgt = points_gdf(targets, lat=target_lat, lon=target_lon).to_crs(CRS_METRIC)
    org = points_gdf(origins, lat=origin_lat, lon=origin_lon).to_crs(CRS_METRIC)
    # buffer de targets y join espacial (¿algún origen cae en cobertura de algún target?)
    tgt_buf = tgt.copy()
    tgt_buf["geometry"] = tgt_buf.geometry.buffer(radius_km * 1000.0)
    joined = gpd.sjoin(org, tgt_buf[["geometry"]], how="inner", predicate="within")
    covered = int(joined.index.nunique())
    total = len(origins)
    return {
        "origins": total,
        "targets": len(targets),
        "covered": covered,
        "coverage_ratio": round(covered / total, 4) if total else 0.0,
        "radius_km": radius_km,
    }
