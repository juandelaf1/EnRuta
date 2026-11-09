"""Tests m2m (D5) para endpoints de integración."""
import sys
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_evaluate_accepts_m2m_key(monkeypatch):
    monkeypatch.setenv("ENRUTA_M2M_KEYS", "poolar:secret-test-key:logistics:evaluate")
    r = client.post(
        "/matches/evaluate",
        headers={"X-API-Key": "secret-test-key"},
        json={"ofertas": [], "demandas": [], "max_detour_pct": 20, "max_detour_km": 50, "top_k": 10},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 0
    assert body["contract_version"] == "logistics-l1/0.1"


def test_evaluate_rejects_wrong_m2m_scope(monkeypatch):
    monkeypatch.setenv("ENRUTA_M2M_KEYS", "poolar:secret-test-key:other:scope")
    r = client.post(
        "/matches/evaluate",
        headers={"X-API-Key": "secret-test-key"},
        json={"ofertas": [], "demandas": []},
    )
    assert r.status_code == 403


def test_evaluate_rejects_invalid_m2m_and_no_user(monkeypatch):
    monkeypatch.setenv("ENRUTA_M2M_KEYS", "poolar:secret-test-key:logistics:evaluate")
    r = client.post(
        "/matches/evaluate",
        headers={"X-API-Key": "wrong-key"},
        json={"ofertas": [], "demandas": []},
    )
    assert r.status_code == 401
