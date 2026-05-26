import sys
sys.path.insert(0, ".")

from src.database import init_db, get_connection, write_df
from src.ingestors.provincias import PROVINCIAS
from src.ingestors.municipios_data import get_municipios, MUNICIPIOS
import pandas as pd


def step1_provincias():
    conn = get_connection()
    conn.executemany(
        "INSERT OR IGNORE INTO provincias (id, nombre, codigo, comunidad) VALUES (?, ?, ?, ?)",
        PROVINCIAS
    )
    conn.commit()
    print(f"[EnRuta] {len(PROVINCIAS)} provincias cargadas")


def step2_municipios():
    data = get_municipios()
    df = pd.DataFrame(data, columns=["id", "nombre", "provincia_id", "lat", "lon", "poblacion_2024"])
    write_df(df, "municipios", if_exists="replace")
    total_pop = df["poblacion_2024"].sum()
    print(f"[EnRuta] {len(df)} municipios cargados (población total: {total_pop:,})")


def step3_datos_sinteticos():
    """
    Genera datos sintéticos de productores y transportistas para el MVP.
    Basado en distribución real de municipios.
    
    T E C H   D E B T : Sustituir por datos reales de MAPA, MITMA e INE.
    """
    conn = get_connection()
    muns = pd.read_sql("SELECT * FROM municipios", conn)

    import random
    random.seed(42)

    # Productores: aceite, vino, miel, conservas, legumbres
    tipos_producto = [
        "Aceite de oliva", "Vino", "Miel", "Conservas vegetales",
        "Legumbres", "Frutos secos", "Arroz", "Queso artesanal"
    ]
    conn.executescript("PRAGMA foreign_keys=OFF; DELETE FROM matches; DELETE FROM demandas; DELETE FROM ofertas; DELETE FROM transportistas; DELETE FROM productores; PRAGMA foreign_keys=ON;")
    conn.commit()

    pid = 0
    productores_rows = []
    for _, mun in muns.iterrows():
        n = max(1, int(mun["poblacion_2024"] / 50000)) + random.randint(0, 2)
        for _ in range(n):
            pid += 1
            tipo = random.choice(tipos_producto)
            productores_rows.append({
                "id": pid, "nombre": f"Productor {tipo[:10]} {mun['nombre']}",
                "tipo": tipo, "localidad": mun["nombre"],
                "provincia_id": int(mun["provincia_id"]),
                "lat": mun["lat"] + random.uniform(-0.02, 0.02),
                "lon": mun["lon"] + random.uniform(-0.02, 0.02),
            })

    df_prod = pd.DataFrame(productores_rows)
    write_df(df_prod, "productores", if_exists="replace")
    print(f"[EnRuta] {len(df_prod)} productores sintéticos generados")

    # Transportistas: 1-3 por municipio
    tid = 0
    transpo_rows = []
    for _, mun in muns.iterrows():
        n = max(0, int(mun["poblacion_2024"] / 100000)) + random.randint(0, 1)
        for _ in range(n):
            tid += 1
            capacidad = random.choice([500, 1000, 2000, 5000, 10000])
            transpo_rows.append({
                "id": tid, "nombre": f"Transporte {mun['nombre']}",
                "localidad": mun["nombre"],
                "provincia_id": int(mun["provincia_id"]),
                "licencia": f"LOTT-MD-{random.randint(10000,99999)}",
                "capacidad_kg": capacidad,
                "lat": mun["lat"] + random.uniform(-0.02, 0.02),
                "lon": mun["lon"] + random.uniform(-0.02, 0.02),
            })

    df_trans = pd.DataFrame(transpo_rows)
    write_df(df_trans, "transportistas", if_exists="replace")
    print(f"[EnRuta] {len(df_trans)} transportistas sintéticos generados")

    # Ofertas: viajes de los transportistas
    oid = 0
    ofertas_rows = []
    for _, t in df_trans.iterrows():
        n_viajes = random.randint(1, 3)
        for _ in range(n_viajes):
            oid += 1
            dest = muns.sample(1).iloc[0]
            ofertas_rows.append({
                "id": oid,
                "transportista_id": int(t["id"]),
                "origen_localidad": t["localidad"],
                "origen_lat": t["lat"],
                "origen_lon": t["lon"],
                "destino_localidad": dest["nombre"],
                "destino_lat": dest["lat"],
                "destino_lon": dest["lon"],
                "fecha": f"2026-0{random.randint(1,6)}-{random.randint(1,28):02d}",
                "capacidad_disponible_kg": random.randint(100, int(t["capacidad_kg"])),
                "precio_sugerido": round(random.uniform(50, 500), 2),
                "activa": 1 if random.random() > 0.2 else 0,
            })

    df_ofertas = pd.DataFrame(ofertas_rows)
    write_df(df_ofertas, "ofertas", if_exists="replace")
    print(f"[EnRuta] {len(df_ofertas)} ofertas sintéticas generadas")

    # Demandas: pedidos de los productores
    did = 0
    demandas_rows = []
    for _, p in df_prod.iterrows():
        if random.random() > 0.5:
            continue
        did += 1
        dest = muns.sample(1).iloc[0]
        demandas_rows.append({
            "id": did,
            "productor_id": int(p["id"]),
            "origen_localidad": p["localidad"],
            "origen_lat": p["lat"],
            "origen_lon": p["lon"],
            "destino_localidad": dest["nombre"],
            "destino_lat": dest["lat"],
            "destino_lon": dest["lon"],
            "kg": random.randint(50, 2000),
            "producto": p["tipo"],
            "urgente": 1 if random.random() > 0.8 else 0,
            "activa": 1,
        })

    df_demandas = pd.DataFrame(demandas_rows)
    write_df(df_demandas, "demandas", if_exists="replace")
    print(f"[EnRuta] {len(df_demandas)} demandas sintéticas generadas")


def run_pipeline():
    print("=" * 50)
    print("  EnRuta — Pipeline de Ingesta (España)")
    print("=" * 50)

    init_db()
    step1_provincias()
    step2_municipios()
    step3_datos_sinteticos()

    print("=" * 50)
    print("  Pipeline completado")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()
