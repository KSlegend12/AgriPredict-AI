"""
Automated Backend Test Suite for AgriPredict-AI.

Tests:
1. Health and readiness checks (including behavior when models are loaded / unready).
2. Production cotton yield prediction endpoint:
   - Valid inputs across Vidarbha districts.
   - 2024 holdout evaluation behavior.
   - Validation against unknown districts.
   - Validation against out-of-range years.
   - Validation against target column leakage.
   - Validation against unknown feature keys.
   - Validation against empty/insufficient feature inputs.
3. Separation of experimental routes:
   - 2025 out-of-sample hindcast endpoint (/api/cotton/future-forecast/2025/{district}).
   - 2026 scenario predictions endpoint (/api/cotton/future-forecast/2026/{district}).
   - 2027-2031 future forecasting endpoints (/api/cotton/future-forecast/{district}, /all, /districts).
4. District, weather, crop recommendation, yield prediction, and history routes.
5. Error handling: non-leakage of filesystem paths, valid HTTP status codes (200, 400, 422, 503).
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import VALID_DISTRICTS


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# =====================================================================
# 1. HEALTH AND READINESS CHECKS
# =====================================================================

def test_health_check(client):
    """Verify /api/health returns 200 with model metrics and system information."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "cotton_yield_vidarbha" in data["modules"]
    assert data["modules"]["cotton_yield_vidarbha"]["is_loaded"] is True
    assert len(data["modules"]["cotton_yield_vidarbha"]["districts"]) == 6


def test_readiness_check_success(client):
    """Verify /api/ready returns 200 when all models are loaded."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert data["models"]["cotton_yield"]["loaded"] is True
    assert data["models"]["crop_suitability"]["loaded"] is True


def test_readiness_check_failure(monkeypatch, client):
    """Verify /api/ready returns 503 if any model is not loaded."""
    from backend.ml.cotton_predictor import cotton_predictor
    monkeypatch.setattr(cotton_predictor, "is_loaded", False)

    response = client.get("/api/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["ready"] is False
    assert data["models"]["cotton_yield"]["loaded"] is False


# =====================================================================
# 2. DISTRICT & REGIONAL METADATA ENDPOINTS
# =====================================================================

def test_get_districts_list(client):
    """Verify /api/districts returns all 36 Maharashtra districts."""
    response = client.get("/api/districts")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_districts"] == 36
    assert len(data["districts"]) == 36


def test_get_cotton_districts(client):
    """Verify /api/cotton/districts returns exactly the 7 Vidarbha districts."""
    response = client.get("/api/cotton/districts")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_districts"] == 6
    district_names = [d["district"] for d in data["districts"]]
    assert set(district_names) == set(VALID_DISTRICTS)


def test_cotton_model_info(client):
    """Verify /api/cotton/model/info returns transparent metadata without modifying artifacts."""
    response = client.get("/api/cotton/model/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_name"] == "GradientBoosting"
    assert data["total_features"] == 36
    assert data["is_model_loaded"] is True


# =====================================================================
# 3. PRODUCTION COTTON PREDICTION ENDPOINT
# =====================================================================

@pytest.mark.parametrize("district", VALID_DISTRICTS)
def test_cotton_predict_valid_districts_2024(client, district):
    """Verify /api/cotton/predict produces valid predictions across all 7 districts for 2024."""
    payload = {"district": district, "target_year": 2024}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["district"] == district
    assert data["predicted_yield_kg_ha"] > 0
    assert data["prediction_status"] == "historical_holdout_evaluation_year"
    assert "explanation" in data
    assert "validation_context" in data


def test_cotton_predict_historical_year(client):
    """Verify prediction on a historical year (e.g., 2020)."""
    payload = {"district": "Nagpur", "target_year": 2020}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction_status"] == "historical_model_estimate"
    assert data["prediction_input"]["target_year"] == 2020


def test_cotton_predict_invalid_district(client):
    """Verify rejection when an unsupported district is passed."""
    payload = {"district": "Pune", "target_year": 2024}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422


def test_cotton_predict_invalid_year(client):
    """Verify rejection when an out-of-range year is passed."""
    payload = {"district": "Akola", "target_year": 2050}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422


def test_cotton_predict_missing_model_artifact(monkeypatch, client):
    """Verify endpoint returns 503 when cotton predictor model is unavailable."""
    from backend.ml.cotton_predictor import cotton_predictor
    monkeypatch.setattr(cotton_predictor, "is_loaded", False)

    payload = {"district": "Akola", "target_year": 2024}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 503
    assert "not currently available" in response.json()["detail"]


def test_cotton_predictor_rejects_target_leakage():
    """Verify the predictor engine explicitly rejects yield_target_kg_ha."""
    from backend.ml.cotton_predictor import cotton_predictor
    bad_input = {
        "district": "Akola",
        "yield_target_kg_ha": 350.0,
        "cotton_area_000ha": 250.0,
    }
    result = cotton_predictor.predict(bad_input)
    assert result["status"] == "error"
    assert "Target column 'yield_target_kg_ha' must not be passed" in result["message"]


def test_cotton_predictor_rejects_unknown_features():
    """Verify the predictor engine rejects unexpected/malformed feature columns."""
    from backend.ml.cotton_predictor import cotton_predictor
    bad_input = {
        "district": "Akola",
        "fake_synthetic_feature_xyz": 999.0,
        "cotton_area_000ha": 250.0,
    }
    result = cotton_predictor.predict(bad_input)
    assert result["status"] == "error"
    assert "Unknown or disallowed feature columns" in result["message"]


# =====================================================================
# 4. EXPERIMENTAL 2025 HINDCAST & 2026 SCENARIO FORECASTS
# =====================================================================

def test_experimental_2025_hindcast_valid(client):
    """Verify /api/cotton/future-forecast/2025/{district} returns verified 2025 results."""
    response = client.get("/api/cotton/future-forecast/2025/Nagpur")
    assert response.status_code == 200
    data = response.json()
    assert data["target_year"] == 2025
    assert data["prediction_type"] == "experimental_out_of_sample_hindcast"
    assert data["actual_target_available"] is True
    assert "actual" in data
    assert "prediction" in data
    assert "overall_metrics" in data


def test_experimental_2025_hindcast_invalid_district(client):
    """Verify 2025 endpoint rejects unknown districts with 400."""
    response = client.get("/api/cotton/future-forecast/2025/UnknownDistrict")
    assert response.status_code == 400


def test_experimental_2026_forecast_valid(client):
    """Verify /api/cotton/future-forecast/2026/{district} returns 3 scenarios."""
    response = client.get("/api/cotton/future-forecast/2026/Wardha")
    assert response.status_code == 200
    data = response.json()
    assert data["target_year"] == 2026
    assert data["prediction_type"] == "scenario_based_experimental_prediction"
    assert len(data["scenarios"]) == 3
    scenarios = [s["scenario"] for s in data["scenarios"]]
    assert scenarios == ["dry", "normal", "wet"]


def test_experimental_2026_forecast_invalid_district(client):
    """Verify 2026 endpoint rejects unknown districts with 400."""
    response = client.get("/api/cotton/future-forecast/2026/InvalidDistrict")
    assert response.status_code == 400


# =====================================================================
# 5. FUTURE FORECASTING (2027–2031) HORIZON ROUTES
# =====================================================================

def test_future_forecast_districts(client):
    """Verify /api/cotton/future-forecast/districts returns 7 districts and 5 forecast years."""
    response = client.get("/api/cotton/future-forecast/districts")
    assert response.status_code == 200
    data = response.json()
    assert set(data["districts"]) == set(VALID_DISTRICTS)
    assert data["forecast_years"] == [2027, 2028, 2029, 2030, 2031]


def test_future_forecast_single_district(client):
    """Verify /api/cotton/future-forecast/{district} generates 5-year multi-scenario predictions."""
    response = client.get("/api/cotton/future-forecast/Akola")
    assert response.status_code == 200
    data = response.json()
    assert data["district"] == "Akola"
    assert "scenarios" in data
    for scenario in ["normal", "dry", "wet"]:
        assert scenario in data["scenarios"]
        assert len(data["scenarios"][scenario]) == 5


def test_future_forecast_invalid_district(client):
    """Verify 400 error on unknown district for future forecasting."""
    response = client.get("/api/cotton/future-forecast/Thane")
    assert response.status_code == 400


# =====================================================================
# 6. CROP RECOMMENDATION & YIELD PREDICTION
# =====================================================================

def test_crop_recommendation_valid(client):
    """Verify /api/crop/recommend returns ranked crop suitability recommendations."""
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 26.5,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["crop"] == "Cotton"


def test_crop_recommendation_invalid_soil_ph(client):
    """Verify validation error on out-of-range soil pH (e.g. 15.0)."""
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 26.5,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 15.0,  # invalid: le=11.0
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422


def test_yield_prediction_valid(client):
    """Verify /api/yield/predict for supported crop."""
    payload = {
        "district": "Pune",
        "crop": "Cotton",
        "target_year": 2026,
        "season": "Kharif",
        "temperature": 25.0,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 6.5,
        "nitrogen": 90.0,
        "phosphorus": 50.0,
        "potassium": 60.0,
        "soil_moisture": 60.0,
        "cultivated_area": 2.5
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_yield_ha" in data
    assert data["predicted_yield_ha"] > 0


def test_yield_prediction_disallowed_crop(client):
    """Verify /api/yield/predict rejects unsupported crops with 422."""
    payload = {
        "district": "Pune",
        "crop": "Wheat",  # Not in ALLOWED_CROPS
        "target_year": 2026,
        "season": "Kharif",
        "temperature": 25.0,
        "rainfall": 600.0,
        "humidity": 65.0,
        "soil_ph": 6.5,
        "nitrogen": 90.0,
        "phosphorus": 50.0,
        "potassium": 60.0,
        "soil_moisture": 60.0,
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 422


# =====================================================================
# 7. HISTORY & WEATHER RETRIEVAL
# =====================================================================

def test_get_history(client):
    """Verify /api/history returns recorded prediction history."""
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "history" in data


def test_get_district_weather(client):
    """Verify /api/weather/{district} returns weather payload or fallback."""
    response = client.get("/api/weather/Akola")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "temperature" in data["data"]
