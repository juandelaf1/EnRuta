import requests
import pandas as pd
from pathlib import Path
from src.config import DATA_RAW, INE_API_BASE

def download_poblacion_municipal():
    """
    Descarga población por municipio desde el INE (API JSON).
    Tabla ID 573: población por municipio, sexo y año.
    """
    url = f"{INE_API_BASE}/DATOS_TABLA/{INE_POBLACION_ID}"
    print(f"[INE] Descargando población municipal desde {url}...")
    try:
        r = requests.get(url, params={"date": "2024-01-01"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        print(f"[INE] Recibidos {len(data)} registros")
        return data
    except Exception as e:
        print(f"[INE] Error en API: {e}")
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
