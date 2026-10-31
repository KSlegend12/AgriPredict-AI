"""
Unit and integration tests for Future Cotton Yield Forecasting and Data Provenance Audit.
Verifies:
- Case-insensitivity and alias resolution in forecasting endpoints.
- Strict rejection of unsupported districts (HTTP 400).
- Forecast-origin temporal safety: origin year 2024, forecast years 2027-2031 (horizons 3-7).
- Uncertainty bounds validity (lower <= predicted <= upper).
- Transparent provenance metadata and satellite status reporting.
- Authentic SMAP satellite temporal boundary validation (no pre-2018 synthetic fabrication).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_future_forecast_districts(client):
    res = client.get("/api/cotton/future-forecast/districts")
    assert res.status_code == 200
    data = res.json()
    assert "districts" in data
    assert len(data["districts"]) == 6
    assert "forecast_years" in data
    assert data["forecast_years"] == [2027, 2028, 2029, 2030, 2031]
    assert "scenarios" in data
    assert set(data["scenarios"]) == {"normal", "dry", "wet"}

def test_future_forecast_case_insensitivity(client):
    # Lowercase district
    res_lower = client.get("/api/cotton/future-forecast/akola")
    assert res_lower.status_code == 200
    assert res_lower.json()["district"] == "Akola"

    # Mixed-case district
    res_mixed = client.get("/api/cotton/future-forecast/wAsHiM")
    assert res_mixed.status_code == 200
    assert res_mixed.json()["district"] == "Washim"

def test_future_forecast_unsupported_district_rejected(client):
    res = client.get("/api/cotton/future-forecast/Pune")
    assert res.status_code == 400
    assert "Unknown district" in res.text

    res_unknown = client.get("/api/cotton/future-forecast/Atlantis")
    assert res_unknown.status_code == 400
    assert "Unknown district" in res_unknown.text

def test_future_forecast_origin_safety_and_uncertainty(client):
    res = client.get("/api/cotton/future-forecast/Wardha")
    assert res.status_code == 200
    data = res.json()
    assert data["origin_year"] == 2024
    assert data["forecast_years"] == [2027, 2028, 2029, 2030, 2031]
    assert "data_provenance" in data
    assert "satellite_status" in data["data_provenance"]
    assert "future_weather" in data["data_provenance"]

    for sc in ["normal", "dry", "wet"]:
        items = data["scenarios"][sc]
        assert len(items) == 5
        for item in items:
            assert item["year"] in [2027, 2028, 2029, 2030, 2031]
            assert item["horizon_years"] == item["year"] - 2024
            assert item["predicted_yield_kg_ha"] >= 0
            assert item["uncertainty_lower_kg_ha"] <= item["predicted_yield_kg_ha"]
            assert item["predicted_yield_kg_ha"] <= item["uncertainty_upper_kg_ha"]
            assert item["uncertainty_band_kg_ha"] > 0

def test_2025_experimental_hindcast_provenance(client):
    res = client.get("/api/cotton/future-forecast/2025/Amravati")
    assert res.status_code == 200
    data = res.json()
    assert data["target_year"] == 2025
    assert data["district"] == "Amravati"
    assert data["actual_target_available"] is True
    assert "actual" in data
    assert "prediction" in data
    assert "overall_metrics" in data
    assert "MAE_kg_ha" in data["overall_metrics"]

def test_2026_experimental_scenario_provenance(client):
    res = client.get("/api/cotton/future-forecast/2026/Nagpur")
    assert res.status_code == 200
    data = res.json()
    assert data["target_year"] == 2026
    assert data["district"] == "Nagpur"
    assert data["actual_target_available"] is False
    assert "data_provenance" in data
    assert "scenarios" in data
    assert len(data["scenarios"]) == 3

def test_satellite_smap_temporal_boundary_rejection(client):
    # Year 2015 is prior to SMAP availability; must be rejected with 422
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2015,
        "model_version": "candidate_satellite_smap"
    })
    assert res.status_code == 422
    assert "2018–2024" in res.json().get("detail", "")
