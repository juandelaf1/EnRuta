"""Auditoría mínima de integración (no secretos/PII)."""
from __future__ import annotations

import logging
from fastapi import Request

logger = logging.getLogger("enruta.audit")


def audit_integration(request: Request, contract_version: str, outcome: str = "ok", extra: dict | None = None):
    payload = {
        "event": "integration_call",
        "caller": getattr(request.state, "caller", "anonymous"),
        "correlation_id": request.headers.get("X-Correlation-Id") or request.headers.get("X-Request-Id") or "",
        "contract_version": contract_version,
        "method": request.method,
        "path": request.url.path,
        "outcome": outcome,
    }
    if extra:
        payload.update(extra)
    logger.info("audit %s", payload)
