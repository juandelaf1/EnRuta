import sqlite3
import pandas as pd
from pathlib import Path
from src.config import DB_PATH

_conn = None

def get_connection():
    global _conn
    if _conn is not None:
        return _conn
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    _conn = sqlite3.connect(str(DB_PATH))
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA foreign_keys=ON")
    return _conn

def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS provincias (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            comunidad TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS municipios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            provincia_id INTEGER NOT NULL,
            codigo_ine TEXT NOT NULL,
            lat REAL,
            lon REAL,
            poblacion_2024 INTEGER DEFAULT 0,
            FOREIGN KEY (provincia_id) REFERENCES provincias(id)
        );

        CREATE TABLE IF NOT EXISTS transportistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            localidad TEXT,
            provincia_id INTEGER,
            licencia TEXT,
            capacidad_kg INTEGER DEFAULT 0,
            lat REAL,
            lon REAL,
            FOREIGN KEY (provincia_id) REFERENCES provincias(id)
        );

        CREATE TABLE IF NOT EXISTS productores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            tipo TEXT,
            localidad TEXT,
            provincia_id INTEGER,
            lat REAL,
            lon REAL,
            FOREIGN KEY (provincia_id) REFERENCES provincias(id)
        );

        CREATE TABLE IF NOT EXISTS ofertas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transportista_id INTEGER NOT NULL,
            origen_localidad TEXT,
            origen_lat REAL,
            origen_lon REAL,
            destino_localidad TEXT,
            destino_lat REAL,
            destino_lon REAL,
            fecha TEXT,
            capacidad_disponible_kg REAL,
            precio_sugerido REAL,
            activa INTEGER DEFAULT 1,
            FOREIGN KEY (transportista_id) REFERENCES transportistas(id)
        );

        CREATE TABLE IF NOT EXISTS demandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            productor_id INTEGER NOT NULL,
            origen_localidad TEXT,
            origen_lat REAL,
            origen_lon REAL,
            destino_localidad TEXT,
            destino_lat REAL,
            destino_lon REAL,
            kg REAL,
            producto TEXT,
            urgente INTEGER DEFAULT 0,
            activa INTEGER DEFAULT 1,
            FOREIGN KEY (productor_id) REFERENCES productores(id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oferta_id INTEGER,
            demanda_id INTEGER,
            ahorro_estimado REAL,
            co2_evitado_kg REAL,
            fecha_match TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (oferta_id) REFERENCES ofertas(id),
            FOREIGN KEY (demanda_id) REFERENCES demandas(id)
        );
    """)
    conn.commit()

def write_df(df, table, if_exists="replace"):
    conn = get_connection()
    df.to_sql(table, conn, if_exists=if_exists, index=False)
    conn.commit()

def read_sql(query):
    conn = get_connection()
    return pd.read_sql_query(query, conn)
