import sys
sys.path.insert(0, ".")
import pandas as pd
import functools
from src.database import get_connection, read_sql
from src.geo.engine import distancia_optima, haversine


@functools.lru_cache(maxsize=10000)
def cached_distancia(lat1, lon1, lat2, lon2):
    return distancia_optima(lat1, lon1, lat2, lon2)


def match_all(max_detour_pct=20, max_detour_km=50, top_k=2000):
    conn = get_connection()

    ofertas = read_sql("""
        SELECT o.*, t.nombre as transportista, t.capacidad_kg
        FROM ofertas o
        JOIN transportistas t ON o.transportista_id = t.id
        WHERE o.activa = 1
    """)

    demandas = read_sql("""
        SELECT d.*, p.nombre as productor, p.tipo as producto_tipo
        FROM demandas d
        JOIN productores p ON d.productor_id = p.id
        WHERE d.activa = 1
    """)

    if ofertas.empty or demandas.empty:
        return pd.DataFrame()

    print(f"[Match] Evaluando {len(ofertas)} ofertas x {len(demandas)} demandas con Haversine...")

    candidates = []
    for _, of in ofertas.iterrows():
        for _, de in demandas.iterrows():
            if of["capacidad_disponible_kg"] < de["kg"]:
                continue

            h_transp = haversine(of["origen_lat"], of["origen_lon"],
                                 of["destino_lat"], of["destino_lon"])
            if h_transp == 0:
                continue

            h_desvio = (
                haversine(of["origen_lat"], of["origen_lon"],
                          de["origen_lat"], de["origen_lon"])
                + haversine(de["origen_lat"], de["origen_lon"],
                            de["destino_lat"], de["destino_lon"])
                + haversine(de["destino_lat"], de["destino_lon"],
                            of["destino_lat"], of["destino_lon"])
            )
            extra = h_desvio - h_transp
            if extra < 0:
                extra = 0
            detour_pct = (extra / h_transp) * 100
            extra_km_hav = extra

            # Filtro rápido con Haversine (generoso, 2x los límites)
            if extra > max_detour_km * 2 and detour_pct > max_detour_pct * 2:
                continue

            score_hav = 100 - detour_pct
            cap_ratio = de["kg"] / of["capacidad_disponible_kg"]
            if cap_ratio > 0.8:
                score_hav += 10
            if de["urgente"]:
                score_hav += 15

            candidates.append({
                "oferta_id": int(of["id"]),
                "demanda_id": int(de["id"]),
                "transportista": of["transportista"],
                "productor": de["productor"],
                "producto": de["producto"],
                "ruta": f"{of['origen_localidad']} -> {of['destino_localidad']}",
                "h_orig_lat": of["origen_lat"], "h_orig_lon": of["origen_lon"],
                "h_dest_lat": of["destino_lat"], "h_dest_lon": of["destino_lon"],
                "p_orig_lat": de["origen_lat"], "p_orig_lon": de["origen_lon"],
                "p_dest_lat": de["destino_lat"], "p_dest_lon": de["destino_lon"],
                "extra_km_hav": round(extra_km_hav, 1),
                "detour_pct_hav": round(detour_pct, 1),
                "score_hav": round(score_hav, 1),
                "capacidad_usada_pct": round(cap_ratio * 100, 1),
            })

    if not candidates:
        print("[Match] Sin candidatos tras filtro Haversine")
        return pd.DataFrame()

    df_candidates = pd.DataFrame(candidates).sort_values("score_hav", ascending=False)
    print(f"[Match] {len(df_candidates)} candidatos, usando top {top_k}")

    top = df_candidates.head(top_k)
    matches = []
    for i, (_, row) in enumerate(top.iterrows()):
        if i % 200 == 0:
            print(f"  ... {i}/{min(top_k, len(top))}", end="\r")

        factor_carretera = 1.3

        ruta_directa_km = haversine(row["h_orig_lat"], row["h_orig_lon"],
                                     row["h_dest_lat"], row["h_dest_lon"]) * factor_carretera

        # Ruta con desvío: origen -> pickup -> dropoff -> destino
        ruta_desvio_km = (
            haversine(row["h_orig_lat"], row["h_orig_lon"],
                      row["p_orig_lat"], row["p_orig_lon"])
            + haversine(row["p_orig_lat"], row["p_orig_lon"],
                        row["p_dest_lat"], row["p_dest_lon"])
            + haversine(row["p_dest_lat"], row["p_dest_lon"],
                        row["h_dest_lat"], row["h_dest_lon"])
        ) * factor_carretera

        if ruta_directa_km == 0:
            continue

        extra_km = ruta_desvio_km - ruta_directa_km
        if extra_km < 0:
            extra_km = 0

        detour_pct = (extra_km / ruta_directa_km) * 100

        if extra_km > max_detour_km and detour_pct > max_detour_pct:
            continue

        score = 100 - detour_pct
        cap_ratio = row["capacidad_usada_pct"] / 100
        if cap_ratio > 0.8:
            score += 10
        if row.get("urgente", False):
            score += 15

        co2 = round(ruta_directa_km * 0.3 * 2.6 / 100, 2)

        matches.append({
            "oferta_id": int(row["oferta_id"]),
            "demanda_id": int(row["demanda_id"]),
            "transportista": row["transportista"],
            "productor": row["productor"],
            "producto": row["producto"],
            "ruta": row["ruta"],
            "ruta_original_km": round(ruta_directa_km, 1),
            "extra_km": round(extra_km, 1),
            "detour_pct": round(detour_pct, 1),
            "score": round(score, 1),
            "ahorro_co2_kg": co2,
            "capacidad_usada_pct": round(cap_ratio * 100, 1),
            "fuente": "haversine_1.3x",
        })

    print()
    df = pd.DataFrame(matches)
    if df.empty:
        print("[Match] No se encontraron matches")
        return df

    df = df.sort_values("score", ascending=False)

    conn = get_connection()
    conn.executescript("PRAGMA foreign_keys=OFF; DROP TABLE IF EXISTS matches;")
    conn.execute("""
        CREATE TABLE matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oferta_id INTEGER,
            demanda_id INTEGER,
            ahorro_estimado REAL,
            co2_evitado_kg REAL,
            fecha_match TEXT DEFAULT (datetime('now'))
        )
    """)
    for _, row in df.iterrows():
        conn.execute(
            "INSERT INTO matches (oferta_id, demanda_id, ahorro_estimado, co2_evitado_kg) VALUES (?, ?, ?, ?)",
            (int(row["oferta_id"]), int(row["demanda_id"]), row["extra_km"], row["ahorro_co2_kg"])
        )
    conn.commit()

    print(f"[Match] {len(df)} matches (mejor score: {df.iloc[0]['score']})")
    return df


if __name__ == "__main__":
    df = match_all(top_k=500)
    if not df.empty:
        top = df.head(10)
        for _, r in top.iterrows():
            print(f"  {r['score']:>5}  {r['extra_km']:>5}km  {r['ahorro_co2_kg']:>5}kg  {r['ruta'][:30]:<30}  {r['producto'][:18]:<18}")
        print(f"\nTotal: {len(df)} matches | CO2 total: {df['ahorro_co2_kg'].sum():.0f}kg")
