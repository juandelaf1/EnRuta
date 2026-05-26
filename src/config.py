import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "enruta.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

INE_API_BASE = "https://servicios.ine.es/wstempus/js/ES"
INE_POBLACION_ID = 573  # ID de la tabla de población municipal del INE
