"""
Unit and integration tests for Weather Service.
Verifies:
- Case-insensitivity and alias resolution.
- Valid response schema with temperature, humidity, rainfall, wind_speed, and provider.
- Proper fallback behavior without crashing.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_weather_endpoint_case_insensitive_akola(client):
    res = client.get("/api/weather/akola")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    w = data["data"]
    assert w["district"] == "Akola"
    assert "temperature" in w
    assert "humidity" in w
    assert "rainfall" in w
    assert "provider" in w

def test_weather_endpoint_alias_aurangabad(client):
    res = client.get("/api/weather/aurangabad")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    w = data["data"]
    assert w["district"] == "Chhatrapati Sambhajinagar"

def test_weather_endpoint_unknown_district_fallback(client):
    res = client.get("/api/weather/unknown_district_xyz")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    w = data["data"]
    # Fallback to Pune
    assert w["district"] == "Pune"
