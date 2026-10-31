"""
API Contract and Schema Validation Test Suite.
Verifies request validation, response schemas, error responses (422),
boundary conditions, optional field handling, and model version propagation.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.response_schemas import (
    HealthResponse,
    ReadyResponse,
    DistrictsResponse,
    WeatherResponse,
    CropRecommendResponse,
    YieldPredictResponse,
    CottonPredictResponse,
    CottonDistrictsResponse,
    CottonModelInfoResponse,
    CottonXaiGlobalResponse,
    FutureForecastDistrictsResponse,
    FutureForecastResponse,
    HistoryResponse,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------
# 1. Health and Readiness Contracts
# ---------------------------------------------------------

def test_health_contract(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    validated = HealthResponse.model_validate(data)
    assert validated.status == "online"
    assert validated.app_name == "AgriPredict AI"
    assert validated.geographic_scope == "Maharashtra, India"
    assert "cotton_yield_vidarbha" in validated.modules
    assert "crop_suitability" in validated.modules


def test_ready_contract(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    data = response.json()
    validated = ReadyResponse.model_validate(data)
    assert validated.ready is True
    assert validated.models["cotton_yield"]["loaded"] is True
    assert validated.models["crop_suitability"]["loaded"] is True


# ---------------------------------------------------------
# 2. Districts and Weather Contracts
# ---------------------------------------------------------

def test_districts_contract(client):
    response = client.get("/api/districts")
    assert response.status_code == 200
    data = response.json()
    validated = DistrictsResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.state == "Maharashtra"
    assert validated.total_districts == 36
    assert len(validated.districts) == 36
    district_names = [d.name for d in validated.districts]
    assert "Akola" in district_names
    assert "Pune" in district_names


def test_weather_contract_valid_district(client):
    response = client.get("/api/weather/Akola")
    assert response.status_code == 200
    data = response.json()
    validated = WeatherResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.data.district == "Akola"
    assert isinstance(validated.data.temperature, (int, float))
    assert isinstance(validated.data.humidity, (int, float))
    assert isinstance(validated.data.rainfall, (int, float))
    assert isinstance(validated.data.wind_speed, (int, float))


def test_weather_contract_fallback_district(client):
    response = client.get("/api/weather/UnknownDistrict")
    # Open-Meteo fallback returns standard weather structure for unmapped district
    assert response.status_code == 200
    data = response.json()
    validated = WeatherResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.data.district in ["UnknownDistrict", "Pune"]


# ---------------------------------------------------------
# 3. Crop Recommendation Request Validation & Contract
# ---------------------------------------------------------

def test_crop_recommend_valid(client):
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "wind_speed": 14.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0,
        "irrigation": True,
        "fertilizer_usage": 150.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    validated = CropRecommendResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.district == "Pune"
    assert validated.season == "Kharif"
    assert len(validated.recommendations) > 0
    top = validated.recommendations[0]
    assert top.suitability_percentage >= 0.0
    assert top.rank == 1
    assert top.factor_scores.temperature >= 0.0


def test_crop_recommend_invalid_ph(client):
    # soil_ph ge=3.0, le=11.0
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 13.5,  # Invalid
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("soil_ph" in err["loc"] for err in errors)


def test_crop_recommend_out_of_range_temperature(client):
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 68.0,  # ge=0, le=55
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("temperature" in err["loc"] for err in errors)


def test_crop_recommend_missing_required_fields(client):
    payload = {
        "district": "Pune",
        "season": "Kharif"
        # Missing required meteorological fields: temperature, rainfall, humidity
        # (Soil parameters are optional with Phase 9 Soil Health Card fallbacks)
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    missing = {err["loc"][-1] for err in errors if err["type"] == "missing"}
    assert {"temperature", "rainfall", "humidity"}.issubset(missing)


def test_crop_recommend_incorrect_data_types(client):
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": "very_hot",  # String instead of float
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("temperature" in err["loc"] for err in errors)


def test_crop_recommend_unsupported_district(client):
    payload = {
        "district": "NewYork",  # Not in 36 Maharashtra districts
        "season": "Kharif",
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("district" in err["loc"] for err in errors)


def test_crop_recommend_unsupported_season(client):
    payload = {
        "district": "Pune",
        "season": "Autumn",  # Valid are Kharif, Rabi, Summer
        "temperature": 27.5,
        "rainfall": 680.0,
        "humidity": 72.0,
        "soil_ph": 6.8,
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 55.0,
        "soil_moisture": 60.0
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("season" in err["loc"] for err in errors)


# ---------------------------------------------------------
# 4. Yield Prediction Contract
# ---------------------------------------------------------

def test_yield_predict_valid(client):
    payload = {
        "district": "Pune",
        "crop": "Cotton",
        "target_year": 2026,
        "season": "Kharif",
        "temperature": 27.0,
        "rainfall": 650.0,
        "humidity": 70.0,
        "soil_ph": 6.5,
        "nitrogen": 80.0,
        "phosphorus": 45.0,
        "potassium": 60.0,
        "soil_moisture": 62.0,
        "cultivated_area": 2.5
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    validated = YieldPredictResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.crop == "Cotton"
    assert validated.predicted_yield_ha > 0.0
    assert validated.total_production_tonnes is not None


def test_yield_predict_invalid_crop(client):
    payload = {
        "district": "Pune",
        "crop": "Pineapple",  # Not in allowed crops (Tomato, Onion, Sugarcane)
        "season": "Kharif",
        "temperature": 27.0,
        "rainfall": 650.0,
        "humidity": 70.0,
        "soil_ph": 6.5,
        "nitrogen": 80.0,
        "phosphorus": 45.0,
        "potassium": 60.0,
        "soil_moisture": 62.0
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("crop" in err["loc"] for err in errors)


# ---------------------------------------------------------
# 5. Vidarbha Cotton Prediction Contracts & Model Versions
# ---------------------------------------------------------

def test_cotton_predict_valid_default_model(client):
    payload = {
        "district": "Akola",
        "target_year": 2024,
        "model_version": "production"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    validated = CottonPredictResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.predicted_yield_kg_ha > 0
    assert validated.model_name != ""
    assert validated.model_version == "production"
    assert validated.district == "Akola"


def test_cotton_predict_candidate_version_propagation(client):
    # Verify Phase 2 champion model version propagation
    version_to_test = "candidate_six_district_dar_deficit_heat_thresh"
    payload = {
        "district": "Amravati",
        "target_year": 2024,
        "model_version": version_to_test
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    validated = CottonPredictResponse.model_validate(data)
    assert validated.model_version == version_to_test
    assert validated.status == "success"
    assert validated.predicted_yield_kg_ha > 0



def test_cotton_predict_unsupported_district(client):
    # Vidarbha cotton is strictly calibrated for Vidarbha 7 districts
    payload = {
        "district": "Mumbai",
        "target_year": 2024,
        "model_version": "production"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("district" in err["loc"] for err in errors)


def test_cotton_predict_target_year_out_of_bounds(client):
    # Year must be ge=1997, le=2024
    payload = {
        "district": "Akola",
        "target_year": 1990,
        "model_version": "production"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("target_year" in err["loc"] for err in errors)


# ---------------------------------------------------------
# 6. Cotton Intelligence & Metadata Endpoints
# ---------------------------------------------------------

def test_cotton_districts_contract(client):
    response = client.get("/api/cotton/districts")
    assert response.status_code == 200
    data = response.json()
    validated = CottonDistrictsResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.total_districts == 6
    assert len(validated.districts) == 6
    district_names = [d.district for d in validated.districts]
    assert "Akola" in district_names
    assert "Yavatmal" not in district_names


def test_cotton_model_info_contract(client):
    response = client.get("/api/cotton/model/info")
    assert response.status_code == 200
    data = response.json()
    validated = CottonModelInfoResponse.model_validate(data)
    assert validated.status == "success"
    assert validated.crop == "Cotton (Gossypium hirsutum)"
    assert validated.total_features > 0
    assert validated.is_model_loaded is True
    # Verify candidate model metadata sections exist in response
    assert "candidate_six_district_dar_deficit_heat_thresh" in data
    assert "candidate_six_district_thermal" in data


def test_cotton_xai_global_contract(client):
    response = client.get("/api/cotton/xai/global")
    assert response.status_code == 200
    data = response.json()
    validated = CottonXaiGlobalResponse.model_validate(data)
    assert validated.status == "success"
    assert "TreeExplainer" in validated.methodology
    assert len(validated.global_feature_importance) > 0
    assert len(validated.top_10_features) == 10


def test_future_forecast_districts_contract(client):
    response = client.get("/api/cotton/future-forecast/districts")
    assert response.status_code == 200
    data = response.json()
    validated = FutureForecastDistrictsResponse.model_validate(data)
    assert len(validated.districts) == 6
    assert validated.forecast_years == [2027, 2028, 2029, 2030, 2031]
    assert set(validated.scenarios) == {"normal", "dry", "wet"}


def test_future_forecast_endpoint_contract(client):
    response = client.get("/api/cotton/future-forecast/Akola")
    assert response.status_code == 200
    data = response.json()
    validated = FutureForecastResponse.model_validate(data)
    assert validated.district == "Akola"
    assert validated.origin_year == 2024
    assert validated.forecast_years == [2027, 2028, 2029, 2030, 2031]
    assert "normal" in validated.scenarios
    assert len(validated.scenarios["normal"]) == 5


# ---------------------------------------------------------
# 7. Prediction History Contract
# ---------------------------------------------------------

def test_history_contract(client):
    response = client.get("/api/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    validated = HistoryResponse.model_validate(data)
    assert validated.status == "success"
    assert isinstance(validated.history, list)
    assert len(validated.history) <= 10
    if len(validated.history) > 0:
        first = validated.history[0]
        assert first.id > 0
        assert first.district != ""
        assert first.timestamp != ""
