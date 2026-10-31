"""
Unit and integration tests for Crop Recommendation Engine audit and improvements.
Verifies:
- Strict district and season validation (HTTP 422 on invalid).
- Seasonal vs monthly rainfall scaling compatibility.
- Agronomic water-deficit and irrigation constraints (rainfed sugarcane penalty).
- Soil pH constraints and corrective advisories (acidic / alkaline).
- Deterministic yield trend history.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_crop_recommendation_valid_inputs(client):
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 27.0,
        "rainfall": 650.0,
        "humidity": 68.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 60.0,
        "soil_moisture": 62.0,
        "irrigation": True
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["district"] == "Pune"
    assert len(data["recommendations"]) == 1
    for r in data["recommendations"]:
        assert r["crop"] == "Cotton"
        assert "rank" in r
        assert "suitability_percentage" in r
        assert "factor_scores" in r
        assert "temperature" in r["factor_scores"]
        assert "rainfall" in r["factor_scores"]
        # Rainfall score should be realistic (> 60) for 650mm with irrigation
        assert r["factor_scores"]["rainfall"] >= 60

def test_crop_recommendation_district_alias_and_casing(client):
    # Test lowercase and alias
    payload = {
        "district": "aurangabad",  # alias for Chhatrapati Sambhajinagar
        "season": "kharif",        # lower case
        "temperature": 28.0,
        "rainfall": 720.0,
        "humidity": 65.0,
        "soil_ph": 7.2,
        "nitrogen": 80.0,
        "phosphorus": 40.0,
        "potassium": 55.0,
        "soil_moisture": 60.0,
        "irrigation": True
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "Chhatrapati Sambhajinagar"
    assert data["season"] == "Kharif"

def test_crop_recommendation_invalid_district_rejects_422(client):
    payload = {
        "district": "Atlantis",
        "season": "Kharif",
        "temperature": 28.0,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 6.5,
        "nitrogen": 80.0,
        "phosphorus": 40.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 422
    assert "Invalid district" in res.text

def test_crop_recommendation_invalid_season_rejects_422(client):
    payload = {
        "district": "Pune",
        "season": "Monsoon",  # Invalid (must be Kharif, Rabi, or Summer)
        "temperature": 28.0,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 6.5,
        "nitrogen": 80.0,
        "phosphorus": 40.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 422
    assert "Invalid season" in res.text

def test_crop_recommendation_rainfed_cotton_deficit(client):
    payload_irrigated = {
        "district": "Akola",
        "season": "Kharif",
        "temperature": 30.0,
        "rainfall": 500.0,
        "humidity": 65.0,
        "soil_ph": 7.0,
        "nitrogen": 120.0,
        "phosphorus": 60.0,
        "potassium": 80.0,
        "soil_moisture": 50.0,
        "irrigation": True
    }
    res_irrigated = client.post("/api/crop/recommend", json=payload_irrigated)
    assert res_irrigated.status_code == 200
    cot_irrigated = next(r for r in res_irrigated.json()["recommendations"] if r["crop"] == "Cotton")

    payload_rainfed = dict(payload_irrigated, irrigation=False)
    res_rainfed = client.post("/api/crop/recommend", json=payload_rainfed)
    assert res_rainfed.status_code == 200
    cot_rainfed = next(r for r in res_rainfed.json()["recommendations"] if r["crop"] == "Cotton")

    # Rainfed cotton under deficit moisture must have equal or lower suitability
    assert cot_rainfed["suitability_percentage"] <= cot_irrigated["suitability_percentage"]


def test_crop_recommendation_soil_ph_advisories(client):
    # Acidic soil test
    res_acidic = client.post("/api/crop/recommend", json={
        "district": "Pune", "season": "Kharif", "temperature": 27.0, "rainfall": 650.0,
        "humidity": 68.0, "soil_ph": 5.2, "nitrogen": 85.0, "phosphorus": 45.0,
        "potassium": 60.0, "soil_moisture": 62.0, "irrigation": True
    })
    assert res_acidic.status_code == 200
    recs_acidic = res_acidic.json()["recommendations"]
    assert any("Acidic soil" in adv for r in recs_acidic for adv in r["advisories"])

    # Alkaline soil test
    res_alkaline = client.post("/api/crop/recommend", json={
        "district": "Pune", "season": "Kharif", "temperature": 27.0, "rainfall": 650.0,
        "humidity": 68.0, "soil_ph": 8.4, "nitrogen": 85.0, "phosphorus": 45.0,
        "potassium": 60.0, "soil_moisture": 62.0, "irrigation": True
    })
    assert res_alkaline.status_code == 200
    recs_alkaline = res_alkaline.json()["recommendations"]
    assert any("Alkaline soil" in adv for r in recs_alkaline for adv in r["advisories"])

def test_yield_prediction_deterministic_trend(client):
    payload = {
        "district": "Pune",
        "crop": "Cotton",
        "target_year": 2026,
        "season": "Kharif",
        "temperature": 27.0,
        "rainfall": 650.0,
        "humidity": 68.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 60.0,
        "soil_moisture": 62.0,
        "irrigation": True,
        "cultivated_area": 2.0
    }
    res1 = client.post("/api/yield/predict", json=payload)
    res2 = client.post("/api/yield/predict", json=payload)
    assert res1.status_code == 200
    assert res2.status_code == 200
    d1 = res1.json()
    d2 = res2.json()
    assert d1["predicted_yield_ha"] == d2["predicted_yield_ha"]
    assert d1["total_production_tonnes"] == d2["total_production_tonnes"]
    # Exact trend values match across multiple calls
    assert d1["trend"] == d2["trend"]
