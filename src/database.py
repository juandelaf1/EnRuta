import sqlite3
import pandas as pd
from pathlib import Path
from src.config import DB_PATH

_conn: sqlite3.Connection | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS provincias (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL, comunidad TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS municipios (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
    provincia_id INTEGER NOT NULL, codigo_ine TEXT NOT NULL,
    lat REAL, lon REAL, poblacion_2024 INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS transportistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT,
    localidad TEXT, provincia_id INTEGER, licencia TEXT,
    capacidad_kg INTEGER DEFAULT 0, lat REAL, lon REAL
);
CREATE TABLE IF NOT EXISTS productores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT,
    tipo TEXT, localidad TEXT, provincia_id INTEGER,
    lat REAL, lon REAL
);
CREATE TABLE IF NOT EXISTS ofertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transportista_id INTEGER NOT NULL,
    origen_localidad TEXT, origen_lat REAL, origen_lon REAL,
    destino_localidad TEXT, destino_lat REAL, destino_lon REAL,
    fecha TEXT, capacidad_disponible_kg REAL,
    precio_sugerido REAL, activa INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS demandas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    productor_id INTEGER NOT NULL,
    origen_localidad TEXT, origen_lat REAL, origen_lon REAL,
    destino_localidad TEXT, destino_lat REAL, destino_lon REAL,
    kg REAL, producto TEXT, urgente INTEGER DEFAULT 0,
    activa INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, nombre TEXT NOT NULL,
    telefono TEXT DEFAULT '', provincia_id INTEGER DEFAULT 0,
    tipo TEXT DEFAULT 'transportista',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS reportes_climaticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL, lat REAL NOT NULL, lon REAL NOT NULL,
    temperatura_c REAL, precipitacion_mm_h REAL,
    viento_kmh REAL, visibilidad_km REAL,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    alerta TEXT DEFAULT 'verde', nota TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    oferta_id INTEGER, demanda_id INTEGER,
    ahorro_estimado REAL, co2_evitado_kg REAL,
    score REAL DEFAULT 0, estado TEXT DEFAULT 'pendiente',
    fecha_match TEXT DEFAULT (datetime('now'))
);
"""

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn

def init_db():
    get_connection()

def write_df(df, table, if_exists="replace"):
    conn = get_connection()
    df.to_sql(table, conn, if_exists=if_exists, index=False)
    conn.commit()

def read_sql(query):
    conn = get_connection()
    return pd.read_sql_query(query, conn)
