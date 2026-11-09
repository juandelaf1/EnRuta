"""Auth m2m mínima (D5). Claves desde entorno, sin loguear secretos.
Formato: ENRUTA_M2M_KEYS='callerA:secretA:scope1|scope2;callerB:secretB:scope1'
Acepta X-API-Key o Authorization: Bearer <secret> (si no es JWT de usuario válido con ese flujo).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Set

from fastapi import Header, HTTPException, Request


@dataclass
class M2MCaller:
    caller: str
    scopes: Set[str]
    key_id: str = ""


def _load_keys() -> list[tuple[str, str, Set[str]]]:
    raw = os.getenv("ENRUTA_M2M_KEYS", "")
    keys = []
    for part in raw.split(";"):
        part = part.strip()
        if not part or part.count(":") < 2:
            continue
        caller, secret, scopes_s = part.split(":", 2)
        keys.append((caller.strip(), secret.strip(), {s.strip() for s in scopes_s.split("|") if s.strip()}))
    # compat: single key
    single = os.getenv("ENRUTA_M2M_API_KEY", "").strip()
    if single:
        caller = os.getenv("ENRUTA_M2M_CALLER", "m2m").strip()
        scopes = {s.strip() for s in os.getenv("ENRUTA_M2M_SCOPES", "logistics:evaluate").split(",") if s.strip()}
        keys.append((caller, single, scopes))
    return keys


def verify_m2m(secret: str, required_scope: Optional[str] = None) -> Optional[M2MCaller]:
    if not secret:
        return None
    for caller, key, scopes in _load_keys():
        if secret == key:
            if required_scope and required_scope not in scopes:
                raise HTTPException(status_code=403, detail="insufficient_scope")
            return M2MCaller(caller=caller, scopes=scopes)
    return None


async def get_m2m_caller(
    request: Request,
    x_api_key: str = Header("", alias="X-API-Key"),
    authorization: str = Header("", alias="Authorization"),
    required_scope: Optional[str] = None,
) -> Optional[M2MCaller]:
    # no exponer secretos: solo verificar
    candidate = (x_api_key or "").strip()
    if not candidate and authorization.startswith("Bearer "):
        candidate = authorization.replace("Bearer ", "", 1).strip()
    if not candidate:
        return None
    caller = verify_m2m(candidate, required_scope=required_scope)
    if caller is None and _load_keys():
        # había config m2m y el candidato no coincidió -> podría ser JWT usuario; dejamos que el caller decida
        return None
    return caller
