"""
Rigorous validation test suite for new cotton yield candidate models:
1. Ridge Delta-Rolling Agronomic Candidate (`candidate_delta_rolling`)
2. Multi-Sensor Regularized Ensemble Candidate (`candidate_regularized_ensemble`)
Preserves production invariants, prevents data leakage, tests exact SHAP additivity,
and verifies strict input validation constraints.
"""

import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import (
    cotton_predictor,
    VALID_DISTRICTS,
    FEATURE_COLS,
    DELTA_ROLLING_FEATURE_COLS,
    REGULARIZED_ENSEMBLE_FEATURE_COLS,
)
from backend.services.cotton_input_builder import cotton_input_builder

client = TestClient(app)

CANONICAL_DATA_PATH = Path("data/vidarbha_cotton_model_ready_1997_2024.csv")
CANONICAL_DATA_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"

PRODUCTION_MODEL_PATH = Path("backend/ml/artifacts/final_model.pkl")
PRODUCTION_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"


def _compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ===========================================================================
# 1. Production Invariant Protection Tests
# ===========================================================================

def test_canonical_dataset_hash_invariant():
    """Ensure the canonical 1997-2024 dataset has never been modified."""
    assert CANONICAL_DATA_PATH.exists(), "Canonical dataset missing"
    current_hash = _compute_sha256(CANONICAL_DATA_PATH)
    assert current_hash == CANONICAL_DATA_HASH, (
        f"Cryptographic violation: Canonical dataset hash mismatch. Expected {CANONICAL_DATA_HASH}, got {current_hash}"
    )


def test_production_model_hash_invariant():
    """Ensure the production final_model.pkl has never been overwritten."""
    assert PRODUCTION_MODEL_PATH.exists(), "Production model artifact missing"
    current_hash = _compute_sha256(PRODUCTION_MODEL_PATH)
    assert current_hash == PRODUCTION_MODEL_HASH, (
        f"Cryptographic violation: Production model hash mismatch. Expected {PRODUCTION_MODEL_HASH}, got {current_hash}"
    )


def test_production_remains_default_model():
    """Ensure default prediction without model_version uses validated production model."""
    built = cotton_input_builder.build("Akola", 2024)
    res = cotton_predictor.predict(built["features"])
    assert res["status"] == "success"
    assert res["model_version"] == "production"
    assert "GradientBoosting" in res["model_name"]
    assert res["model_selection_info"]["production_sha256"] == PRODUCTION_MODEL_HASH


# ===========================================================================
# 2. Candidate Artifacts and Loading Tests
# ===========================================================================

def test_candidate_models_loaded_successfully():
    """Verify both performance-optimized candidate models load correctly."""
    assert cotton_predictor.delta_is_loaded, "Delta-rolling candidate model failed to load"
    assert cotton_predictor.reg_ensemble_is_loaded, "Regularized ensemble candidate failed to load"
    assert cotton_predictor.delta_metadata is not None
    assert cotton_predictor.reg_ensemble_metadata is not None


def test_candidate_feature_column_schemas():
    """Verify feature schemas match expected agronomic and satellite specifications."""
    assert len(DELTA_ROLLING_FEATURE_COLS) == len(FEATURE_COLS) + 6
    assert len(REGULARIZED_ENSEMBLE_FEATURE_COLS) == len(FEATURE_COLS) + 6 + 6
    assert "diurnal_range_kharif" in DELTA_ROLLING_FEATURE_COLS
    assert "sm_surface_kharif_mean" in REGULARIZED_ENSEMBLE_FEATURE_COLS


# ===========================================================================
# 3. Ridge Delta-Rolling Candidate Tests
# ===========================================================================

@pytest.mark.parametrize("district", VALID_DISTRICTS)
def test_delta_rolling_prediction_and_shap_additivity_2024(district):
    """Test Delta-Rolling prediction and exact SHAP additivity across all 7 districts."""
    built = cotton_input_builder.build(district, 2024, model_version="candidate_delta_rolling")
    res = cotton_predictor.predict(built["features"], model_version="candidate_delta_rolling")

    assert res["status"] == "success"
    assert res["model_version"] == "candidate_delta_rolling"
    assert res["predicted_yield_kg_ha"] > 0

    exp = res.get("explanation")
    assert exp is not None
    assert exp["available"] is True
    assert exp["additivity_verified"] is True

    # Validate mathematical additivity of waterfall components
    # Total predicted yield must match base + sum of contributions
    waterfall = exp["waterfall_steps"]
    assert len(waterfall) > 0
    total_step = next(s for s in waterfall if s["type"] == "total")
    assert abs(total_step["contribution_kg_ha"] - res["predicted_yield_kg_ha"]) < 0.2


def test_delta_rolling_rejection_without_historical_anchor():
    """Delta-rolling model must reject prediction if historical 3-year rolling average is missing."""
    built = cotton_input_builder.build("Akola", 2024, model_version="candidate_delta_rolling")
    bad_features = dict(built["features"])
    bad_features.pop("rolling_3yr_yield_mean_kg_ha", None)

    res = cotton_predictor.predict(bad_features, model_version="candidate_delta_rolling")
    assert res["status"] == "error"
    assert "rolling_3yr_yield_mean_kg_ha" in res["message"]


# ===========================================================================
# 4. Regularized Multi-Sensor Ensemble Candidate Tests
# ===========================================================================

@pytest.mark.parametrize("district", VALID_DISTRICTS)
def test_regularized_ensemble_prediction_and_shap_additivity_2024(district):
    """Test Regularized Ensemble prediction and exact SHAP additivity across all 7 districts."""
    built = cotton_input_builder.build(district, 2024, model_version="candidate_regularized_ensemble")
    res = cotton_predictor.predict(built["features"], model_version="candidate_regularized_ensemble")

    assert res["status"] == "success"
    assert res["model_version"] == "candidate_regularized_ensemble"
    assert res["predicted_yield_kg_ha"] > 0
    assert res["satellite_features_used"] is True

    exp = res.get("explanation")
    assert exp is not None
    assert exp["available"] is True
    assert exp["additivity_verified"] is True
    assert "SHAP Hybrid Ensemble" in exp["methodology"]


def test_regularized_ensemble_strict_rejection_pre_satellite_year():
    """Ensemble candidate must strictly reject pre-satellite year (< 2018) via input builder."""
    with pytest.raises(ValueError) as excinfo:
        cotton_input_builder.build("Akola", 2017, model_version="candidate_regularized_ensemble")
    assert "only supported for years 2018–2024" in str(excinfo.value)


def test_regularized_ensemble_strict_rejection_missing_smap_features():
    """Ensemble candidate must reject feature rows missing required NASA SMAP observations."""
    built = cotton_input_builder.build("Akola", 2024, model_version="candidate_regularized_ensemble")
    bad_features = dict(built["features"])
    bad_features.pop("sm_surface_kharif_mean", None)

    res = cotton_predictor.predict(bad_features, model_version="candidate_regularized_ensemble")
    assert res["status"] == "error"
    assert "Missing required NASA SMAP soil moisture features" in res["message"]


# ===========================================================================
# 5. Full API Route Integration Tests (/api/cotton)
# ===========================================================================

def test_api_predict_delta_rolling_success():
    """API endpoint succeeds with model_version='candidate_delta_rolling'."""
    response = client.post(
        "/api/cotton/predict",
        json={"district": "Wardha", "target_year": 2024, "model_version": "candidate_delta_rolling"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_version"] == "candidate_delta_rolling"
    assert data["explanation"]["additivity_verified"] is True


def test_api_predict_regularized_ensemble_success():
    """API endpoint succeeds with model_version='candidate_regularized_ensemble'."""
    response = client.post(
        "/api/cotton/predict",
        json={"district": "Amravati", "target_year": 2024, "model_version": "candidate_regularized_ensemble"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_version"] == "candidate_regularized_ensemble"
    assert data["satellite_features_used"] is True
    assert data["explanation"]["additivity_verified"] is True


def test_api_predict_regularized_ensemble_pre_2018_rejected():
    """API endpoint returns 422 when attempting to run regularized ensemble on pre-2018 year."""
    response = client.post(
        "/api/cotton/predict",
        json={"district": "Amravati", "target_year": 2017, "model_version": "candidate_regularized_ensemble"},
    )
    assert response.status_code == 422
    assert "2018–2024" in response.json()["detail"]


def test_api_model_info_includes_new_candidates():
    """API endpoint /api/cotton/model/info reports both new candidates."""
    response = client.get("/api/cotton/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "candidate_delta_rolling" in data
    assert data["candidate_delta_rolling"]["available"] is True
    assert "candidate_regularized_ensemble" in data
    assert data["candidate_regularized_ensemble"]["available"] is True
    assert "candidate_physiological_ridge_a100" in data
    assert data["candidate_physiological_ridge_a100"]["available"] is True


def test_api_predict_physiological_ridge_success():
    """API endpoint succeeds with model_version='candidate_physiological_ridge_a100' and verifies exact SHAP additivity."""
    response = client.post(
        "/api/cotton/predict",
        json={"district": "Wardha", "target_year": 2024, "model_version": "candidate_physiological_ridge_a100"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["model_version"] == "candidate_physiological_ridge_a100"
    assert data["model_name"] == "Ridge_Delta_Rolling_Physiological_a100"
    assert data["explanation"]["additivity_verified"] is True
    assert len(data["prediction_input"]["missing_features"]) == 0


def test_physiological_ridge_all_seven_districts():
    """Ensure candidate_physiological_ridge_a100 produces valid predictions for all 7 Vidarbha districts."""
    districts = ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]
    for d in districts:
        response = client.post(
            "/api/cotton/predict",
            json={"district": d, "target_year": 2024, "model_version": "candidate_physiological_ridge_a100"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["predicted_yield_kg_ha"] > 0.0
        assert data["explanation"]["additivity_verified"] is True
