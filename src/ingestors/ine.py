import requests
import pandas as pd
from pathlib import Path
from src.config import DATA_RAW, INE_API_BASE, INE_POBLACION_ID

def download_poblacion_municipal(table_id=None):
    """
    Descarga población por municipio desde el INE (API JSON, best-effort).
    La API Tempus3 y los IDs de tabla cambian; si falla, usar la base municipal estática (municipios_data).
    """
    table_id = table_id or INE_POBLACION_ID
    url = f"{INE_API_BASE}/DATOS_TABLA/{table_id}"
    print(f"[INE] Descargando población municipal desde {url} (best-effort)...")
    try:
        r = requests.get(url, params={"nult": 1}, timeout=30)
        if r.status_code != 200:
            print(f"[INE] API no disponible/tabla inválida (HTTP {r.status_code}); usando fallback estático.")
            return None
        try:
            data = r.json()
        except ValueError:
            print("[INE] Respuesta no JSON; usando fallback estático.")
            return None
        if isinstance(data, dict) and data.get("status"):
            print(f"[INE] API devolvió estado {data.get('status')}; usando fallback estático.")
            return None
        if not isinstance(data, list):
            print("[INE] Formato inesperado; usando fallback estático.")
            return None
        print(f"[INE] Recibidos {len(data)} registros")
        return data
    except Exception as e:
        print(f"[INE] Error en API: {e}; usando fallback estático.")
        return None

def parse_poblacion_ine(raw):
    """Procesa JSON del INE a DataFrame con municipio + población."""
    rows = []
    for entry in raw:
        try:
            nombre = entry.get("Nombre", "")
            if not nombre:
                continue
            # El INE devuelve la población en los valores
            valores = entry.get("Data", [])
            poblacion = 0
            for v in valores:
                if v.get("Anyo") == 2024:
                    poblacion = int(v.get("Valor", 0))
                    break

            # Extraer código de municipio
            cod = entry.get("Id", "")
            rows.append({
                "nombre": nombre.strip(),
                "codigo_ine": str(cod).strip(),
                "poblacion": poblacion,
            })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    print(f"[INE] Procesados {len(df)} municipios")
    return df

def save_poblacion_csv(df):
    path = DATA_RAW / "ine_poblacion_municipios.csv"
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[INE] Guardado en {path}")
    return path

def load_poblacion_from_csv():
    path = DATA_RAW / "ine_poblacion_municipios.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

def load_fallback():
    """Carga datos locales de población si la API falla."""
    path = DATA_RAW / "ine_poblacion_municipios.csv"
    if path.exists():
        print("[INE] Usando datos locales")
        return pd.read_csv(path)
    print("[INE] No hay datos locales. Descarga la API o coloca el CSV manualmente.")
    return pd.DataFrame()
