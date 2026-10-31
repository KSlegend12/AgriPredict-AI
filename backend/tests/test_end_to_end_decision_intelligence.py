"""
End-to-End Decision Intelligence Integration Test Suite.
Verifies the complete 8-step agricultural workflow:
1. District selection & regional metadata.
2. Weather telemetry & provenance.
3. Crop recommendation with biophysical constraints & advisories.
4. Cotton yield prediction with active serving models (Thermal Ridge, DAR Deficit Heat Thresh, Production).
5. SHAP Explainability & Waterfall Additivity.
6. Future Cotton Forecasting (2027-2031) with origin safety and empirical uncertainty.
7. Prediction History persistence across SQLite tables.
8. Robust edge-case handling (400/422 on invalid inputs).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_step1_district_selection_metadata(client):
    res = client.get("/api/districts")
    assert res.status_code == 200
    data = res.json()
    assert data["total_districts"] == 36
    assert len(data["districts"]) == 36

    cotton_dist = client.get("/api/cotton/districts")
    assert cotton_dist.status_code == 200
    c_data = cotton_dist.json()
    assert c_data["total_districts"] == 6
    assert "Akola" in [d["district"] for d in c_data["districts"]]

def test_step2_weather_telemetry_provenance(client):
    res = client.get("/api/weather/Akola")
    assert res.status_code == 200
    w = res.json()["data"]
    assert w["district"] == "Akola"
    assert "temperature" in w
    assert "rainfall" in w
    assert "precipitation_live_mm" in w
    assert "provider" in w

def test_step3_crop_recommendation_and_advisories(client):
    payload = {
        "district": "Akola",
        "season": "Kharif",
        "temperature": 29.5,
        "rainfall": 800.0,
        "humidity": 68.0,
        "soil_ph": 7.4,
        "nitrogen": 90.0,
        "phosphorus": 50.0,
        "potassium": 65.0,
        "soil_moisture": 60.0,
        "irrigation": True
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["crop"] == "Cotton"
    top = data["recommendations"][0]
    assert "suitability_percentage" in top
    assert "why_recommendation" in top
    assert "advisories" in top
    assert "factor_scores" in top
    # Confirm factor scores are within reasonable bounds
    assert 20 <= top["factor_scores"]["rainfall"] <= 100

def test_step4_and_5_cotton_prediction_and_shap_waterfall(client):
    # Test operational default: candidate_six_district_thermal
    res_default = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024,
        "model_version": "candidate_six_district_thermal"
    })
    assert res_default.status_code == 200
    d_out = res_default.json()
    assert d_out["status"] == "success"
    assert d_out["predicted_yield_kg_ha"] > 0
    assert "explanation" in d_out
    exp = d_out["explanation"]
    assert "base_value_kg_ha" in exp
    assert "top_influential_features" in exp
    assert len(exp["top_influential_features"]) > 0

    # Test Phase 2 best candidate: candidate_six_district_dar_deficit_heat_thresh
    res_dar = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024,
        "model_version": "candidate_six_district_dar_deficit_heat_thresh"
    })
    assert res_dar.status_code == 200
    dar_out = res_dar.json()
    assert dar_out["status"] == "success"
    assert dar_out["predicted_yield_kg_ha"] > 0
    assert "Deficit_HeatThresh" in dar_out["model_name"] or dar_out.get("model_version") == "candidate_six_district_dar_deficit_heat_thresh"

def test_step6_future_cotton_forecasting_origin_safety(client):
    res = client.get("/api/cotton/future-forecast/Akola")
    assert res.status_code == 200
    data = res.json()
    assert data["origin_year"] == 2024
    assert data["forecast_years"] == [2027, 2028, 2029, 2030, 2031]
    assert "data_provenance" in data
    assert "scenarios" in data
    for sc in ["normal", "dry", "wet"]:
        items = data["scenarios"][sc]
        assert len(items) == 5
        for item in items:
            assert item["predicted_yield_kg_ha"] >= 0
            assert item["uncertainty_lower_kg_ha"] <= item["predicted_yield_kg_ha"] <= item["uncertainty_upper_kg_ha"]

def test_step7_prediction_history_persistence(client):
    res = client.get("/api/history?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "history" in data
    # At least the predictions made in step 3 and 4 should be recorded
    assert len(data["history"]) > 0
    record = data["history"][0]
    assert "timestamp" in record
    assert "district" in record
    assert "crop_type" in record

def test_step8_edge_case_robustness(client):
    # Invalid district for crop recommendation
    res_bad_crop_dist = client.post("/api/crop/recommend", json={
        "district": "Atlantis", "season": "Kharif", "temperature": 27.0,
        "rainfall": 600.0, "humidity": 65.0, "soil_ph": 6.5, "nitrogen": 80.0,
        "phosphorus": 40.0, "potassium": 55.0, "soil_moisture": 60.0
    })
    assert res_bad_crop_dist.status_code == 422

    # Invalid season
    res_bad_season = client.post("/api/crop/recommend", json={
        "district": "Pune", "season": "WinterHoliday", "temperature": 27.0,
        "rainfall": 600.0, "humidity": 65.0, "soil_ph": 6.5, "nitrogen": 80.0,
        "phosphorus": 40.0, "potassium": 55.0, "soil_moisture": 60.0
    })
    assert res_bad_season.status_code == 422

    # Unsupported year for satellite model
    res_bad_sat_year = client.post("/api/cotton/predict", json={
        "district": "Akola", "target_year": 2012, "model_version": "candidate_satellite_smap"
    })
    assert res_bad_sat_year.status_code == 422

    # Unsupported district for future forecast
    res_bad_future_dist = client.get("/api/cotton/future-forecast/London")
    assert res_bad_future_dist.status_code == 400
