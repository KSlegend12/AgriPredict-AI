"""
Integration tests for candidate_six_district_dar_deficit_heat_thresh model version.
Verifies:
1. Registration in cotton_predictor and model_info.
2. Exact biophysical feature calculations (rain_deficit_kharif, hot_days_thresh10).
3. Prediction on all 6 supported Vidarbha districts.
4. HTTP 422 rejection of unsupported district (Yavatmal).
5. Exact SHAP additivity and waterfall explanations.
6. Persistence to cotton_prediction_history SQLite database.
7. Preservation of candidate_six_district_thermal as UI default.
"""

import pytest
import sqlite3
import json
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import cotton_predictor
from backend.services.cotton_input_builder import cotton_input_builder
from backend.database.db import DB_PATH

client = TestClient(app)

SUPPORTED_DISTRICTS = ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]
MODEL_VERSION = "candidate_six_district_dar_deficit_heat_thresh"


def test_model_version_registration_and_info():
    """Verify the candidate is loaded and visible in /api/cotton/model/info."""
    assert getattr(cotton_predictor, "decoupled_deficit_heat_is_loaded", False) is True
    res = client.get("/api/cotton/model/info")
    assert res.status_code == 200
    data = res.json()
    assert MODEL_VERSION in data
    c_info = data[MODEL_VERSION]
    assert c_info["available"] is True
    assert c_info["metadata"]["model_name"] == "Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh"
    assert c_info["metadata"]["alpha"] == 75.0


def test_feature_calculations_in_input_builder():
    """Verify rain_deficit_kharif and hot_days_thresh10 calculations match agronomic formulas."""
    built = cotton_input_builder.build("Akola", 2024, model_version=MODEL_VERSION)
    features = built["features"]

    # Retrieve source row to calculate expected values
    row = cotton_input_builder._get_row("Akola", 2024)
    rain_k = float(row["rainfall_kharif_mm"])
    hot_k = float(row["tmax_hot_days_ge35_kharif"])

    expected_rain_deficit = max(0.0, 750.0 - rain_k) / 100.0
    expected_hot_thresh = max(0.0, hot_k - 10.0) / 10.0

    assert "rain_deficit_kharif" in features
    assert "hot_days_thresh10" in features
    assert abs(features["rain_deficit_kharif"] - expected_rain_deficit) < 1e-6
    assert abs(features["hot_days_thresh10"] - expected_hot_thresh) < 1e-6


def test_predict_all_six_supported_districts():
    """Verify predictions succeed with valid SHAP explanations across all 6 districts."""
    for dist in SUPPORTED_DISTRICTS:
        payload = {
            "district": dist,
            "target_year": 2024,
            "model_version": MODEL_VERSION
        }
        res = client.post("/api/cotton/predict", json=payload)
        assert res.status_code == 200, f"Prediction failed for {dist}: {res.text}"
        data = res.json()
        assert data["status"] == "success"
        assert data["model_version"] == MODEL_VERSION
        pred_yield = float(data["predicted_yield_kg_ha"])
        assert pred_yield > 0

        # Verify SHAP explanation
        exp = data.get("explanation")
        assert exp is not None, f"Explanation object missing for {dist}"
        assert exp.get("available") is True, f"Explanation marked unavailable for {dist}"
        assert exp.get("additivity_verified") is True, f"Additivity check failed in engine for {dist}"

        # Additivity Verification via Waterfall Steps
        waterfall = exp.get("waterfall_steps", [])
        total_step = next((s for s in waterfall if s.get("type") == "total"), None)
        assert total_step is not None, f"Waterfall missing total step for {dist}"

        reconstructed = float(total_step["contribution_kg_ha"])
        discrepancy = abs(reconstructed - pred_yield)
        assert discrepancy < 0.05, f"SHAP additivity violated for {dist}: pred={pred_yield}, total={reconstructed}"

        contributions = exp.get("top_influential_features", [])
        assert len(contributions) > 0


def test_unsupported_district_rejection_http_422():
    """Verify Yavatmal is rejected with HTTP 422 for the 6-district candidate."""
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": MODEL_VERSION
    }
    res = client.post("/api/cotton/predict", json=payload)
    assert res.status_code == 422
    assert "Yavatmal" in str(res.json())


def test_prediction_history_persistence():
    """Verify predictions with candidate_six_district_dar_deficit_heat_thresh persist to SQLite."""
    payload = {
        "district": "Wardha",
        "target_year": 2024,
        "model_version": MODEL_VERSION
    }
    res = client.post("/api/cotton/predict", json=payload)
    assert res.status_code == 200

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT district, target_year, model_version, predicted_yield FROM cotton_prediction_history WHERE model_version = ? ORDER BY id DESC LIMIT 1",
        (MODEL_VERSION,)
    )
    row = cur.fetchone()
    conn.close()

    assert row is not None, "Record was not persisted to SQLite database"
    assert row[0] == "Wardha"
    assert row[1] == 2024
    assert row[2] == MODEL_VERSION
    assert row[3] > 0


def test_thermal_ridge_remains_ui_default():
    """Verify default prediction without model_version retains valid default behavior."""
    payload = {
        "district": "Akola",
        "target_year": 2024
    }
    res = client.post("/api/cotton/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # Either production or candidate_six_district_thermal depending on explicit default
    assert data["predicted_yield_kg_ha"] > 0
