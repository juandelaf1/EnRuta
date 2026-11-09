import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_has_contract():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["contract_version"] == "logistics-l1/0.1"
    assert "capabilities" in body
    assert body["capabilities"].get("matches_evaluate_stateless") is True


def test_health_echoes_correlation_id():
    r = client.get("/health", headers={"X-Correlation-Id": "test-cid-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Correlation-Id") == "test-cid-123"
