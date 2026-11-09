"""Convención de procedencia (P1). Ver docs/PROVENANCE_CONVENTION.md (raíz workspace)."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict


class Procedencia(str, Enum):
    OBSERVADO = "observado"
    ESTIMADO = "estimado"
    SINTETICO = "sintetico"  # alias de simulado
    SIMULADO = "simulado"
    MIXTO = "mixto"  # observado + estimado (p.ej. agregaciones)


def tag(procedencia: str, **meta: Any) -> Dict[str, Any]:
    """Etiqueta de procedencia portable para respuestas/artefactos."""
    out = {"procedencia": procedencia}
    out.update({k: v for k, v in meta.items() if v is not None})
    return out


def ensure_procedencia(value: str | None, default: str = Procedencia.ESTIMADO.value) -> str:
    if not value:
        return default
    v = value.lower()
    for p in Procedencia:
        if v == p.value or v.startswith(p.value):
            return value
    return value  # permitir descripciones compuestas, pero no vacías
