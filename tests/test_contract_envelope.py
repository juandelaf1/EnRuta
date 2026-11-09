"""Backward-compatible envelope dual-read for logistics.evaluate_matches (dev-stage)."""
import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_evaluate_accepts_ecosystem_envelope(monkeypatch):
    monkeypatch.setenv("ENRUTA_M2M_KEYS", "poolar:secret-test-key:logistics:evaluate")
    r = client.post(
        "/matches/evaluate",
        headers={"X-API-Key": "secret-test-key", "X-Correlation-Id": "cid-env-1"},
        json={
            "contract_version": "logistics-l1/0.1",
            "capability_id": "logistics.evaluate_matches",
            "correlation_id": "cid-env-1",
            "payload": {"ofertas": [], "demandas": [], "options": {"top_k": 10}},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 0
    assert body["contract_version"] == "logistics-l1/0.1"
    assert body.get("capability_id") == "logistics.evaluate_matches"
    assert body.get("correlation_id") == "cid-env-1"
    assert body.get("status") == "ok"
    assert body.get("data_status") == "estimated"