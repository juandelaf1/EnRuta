"""Pruebas de seguridad P0 para EnRuta.

Verifica autenticación en rutas de demandas y ofertas.
"""
import sys
sys.path.insert(0, ".")

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def _register_or_login(email, password, data):
    r = client.post("/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    r = client.post("/auth/register", json=data)
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def token_transportista():
    return _register_or_login(
        "tpte@enruta.com", "test123",
        {"email": "tpte@enruta.com", "password": "test123", "nombre": "Test Transportista", "tipo": "transportista", "provincia_id": 28},
    )


@pytest.fixture(scope="module")
def token_productor():
    return _register_or_login(
        "prod@enruta.com", "test123",
        {"email": "prod@enruta.com", "password": "test123", "nombre": "Test Productor", "tipo": "productor", "provincia_id": 4},
    )


def test_list_demandas_accessible_without_auth():
    """GET /demandas es listado público (no requiere auth en implementación actual)."""
    response = client.get("/demandas")
    assert response.status_code == 200


def test_create_demanda_without_auth_returns_401():
    """POST /demandas sin token devuelve 401."""
    demanda = {
        "origen_localidad": "Zaragoza", "origen_lat": 41.6488, "origen_lon": -0.8891,
        "destino_localidad": "Madrid", "destino_lat": 40.4168, "destino_lon": -3.7038,
        "kg": 200, "producto": "Aceite", "urgente": 1,
    }
    response = client.post("/demandas", json=demanda)
    assert response.status_code in (401, 422)


def test_create_oferta_without_auth_returns_401():
    """POST /ofertas sin token devuelve 401."""
    oferta = {
        "origen_localidad": "Madrid", "origen_lat": 40.4168, "origen_lon": -3.7038,
        "destino_localidad": "Barcelona", "destino_lat": 41.3874, "destino_lon": 2.1686,
        "fecha": "2026-06-01", "capacidad_disponible_kg": 5000, "precio_sugerido": 200,
    }
    response = client.post("/ofertas", json=oferta)
    assert response.status_code in (401, 422)


def test_create_demanda_wrong_role_returns_403(token_transportista):
    """Transportista no puede crear demanda."""
    headers = {"Authorization": f"Bearer {token_transportista}"}
    demanda = {
        "origen_localidad": "Zaragoza", "origen_lat": 41.6488, "origen_lon": -0.8891,
        "destino_localidad": "Madrid", "destino_lat": 40.4168, "destino_lon": -3.7038,
        "kg": 200, "producto": "Aceite", "urgente": 1,
    }
    response = client.post("/demandas", json=demanda, headers=headers)
    assert response.status_code == 403


def test_create_oferta_wrong_role_returns_403(token_productor):
    """Productor no puede crear oferta."""
    headers = {"Authorization": f"Bearer {token_productor}"}
    oferta = {
        "origen_localidad": "Madrid", "origen_lat": 40.4168, "origen_lon": -3.7038,
        "destino_localidad": "Barcelona", "destino_lat": 41.3874, "destino_lon": 2.1686,
        "fecha": "2026-06-01", "capacidad_disponible_kg": 5000, "precio_sugerido": 200,
    }
    response = client.post("/ofertas", json=oferta, headers=headers)
    assert response.status_code == 403


def test_create_demanda_with_auth_returns_201(token_productor):
    """Productor puede crear demanda con auth."""
    headers = {"Authorization": f"Bearer {token_productor}"}
    demanda = {
        "origen_localidad": "Zaragoza", "origen_lat": 41.6488, "origen_lon": -0.8891,
        "destino_localidad": "Madrid", "destino_lat": 40.4168, "destino_lon": -3.7038,
        "kg": 200, "producto": "Aceite", "urgente": 1,
    }
    response = client.post("/demandas", json=demanda, headers=headers)
    assert response.status_code in (200, 201)


def test_create_oferta_with_auth_returns_201(token_transportista):
    """Transportista puede crear oferta con auth."""
    headers = {"Authorization": f"Bearer {token_transportista}"}
    oferta = {
        "origen_localidad": "Madrid", "origen_lat": 40.4168, "origen_lon": -3.7038,
        "destino_localidad": "Barcelona", "destino_lat": 41.3874, "destino_lon": 2.1686,
        "fecha": "2026-06-01", "capacidad_disponible_kg": 5000, "precio_sugerido": 200,
    }
    response = client.post("/ofertas", json=oferta, headers=headers)
    assert response.status_code in (200, 201)


def test_get_demanda_nonexistent_returns_404():
    """GET /demandas/{id} inexistente devuelve 404."""
    response = client.get("/demandas/99999")
    assert response.status_code == 404


def test_get_oferta_nonexistent_returns_404():
    """GET /ofertas/{id} inexistente devuelve 404."""
    response = client.get("/ofertas/99999")
    assert response.status_code == 404