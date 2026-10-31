"""
Automated tests for the Six-District Decoupled Agronomic Ridge Candidate.
Verifies:
1. Candidate model loading and metadata integrity.
2. Inference across all six supported districts (Akola, Amravati, Buldhana, Nagpur, Wardha, Washim).
3. SHAP local explanation generation and exact mathematical additivity (|total_step - y_pred| < 0.05).
4. Enforcement of Yavatmal restriction (HTTP 422).
5. Unaltered protected hashes (canonical CSV & production model).
"""

import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import (
    cotton_predictor,
    DATA_PATH,
    MODEL_PATH,
    DECOUPLED_AGRONOMIC_MODEL_PATH,
    DECOUPLED_AGRONOMIC_METADATA_PATH,
)

client = TestClient(app)

CANONICAL_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PROD_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"
SIX_DISTRICTS = ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]


def test_protected_hashes_unaltered():
    with open(DATA_PATH, "rb") as f:
        h_data = hashlib.sha256(f.read()).hexdigest()
    with open(MODEL_PATH, "rb") as f:
        h_model = hashlib.sha256(f.read()).hexdigest()
    assert h_data == CANONICAL_HASH, f"Dataset hash mismatch: {h_data}"
    assert h_model == PROD_MODEL_HASH, f"Model hash mismatch: {h_model}"


def test_candidate_artifacts_exist_and_loaded():
    assert Path(DECOUPLED_AGRONOMIC_MODEL_PATH).exists()
    assert Path(DECOUPLED_AGRONOMIC_METADATA_PATH).exists()
    assert getattr(cotton_predictor, "decoupled_agronomic_is_loaded", False) is True


@pytest.mark.parametrize("dist", SIX_DISTRICTS)
def test_decoupled_agronomic_inference_and_shap_additivity(dist):
    payload = {
        "district": dist,
        "target_year": 2024,
        "model_version": "candidate_six_district_decoupled_agronomic",
    }
    res = client.post("/api/cotton/predict", json=payload)
    assert res.status_code == 200, f"Inference failed for {dist}: {res.text}"

    data = res.json()
    assert data["status"] == "success"
    assert data["model_version"] == "candidate_six_district_decoupled_agronomic"

    pred_yield = float(data["predicted_yield_kg_ha"])
    assert 100.0 <= pred_yield <= 1000.0, f"Unreasonable prediction for {dist}: {pred_yield}"

    # SHAP Explanation Verification
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


def test_yavatmal_rejection_for_decoupled_candidate():
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": "candidate_six_district_decoupled_agronomic",
    }
    res = client.post("/api/cotton/predict", json=payload)
    assert res.status_code == 422, f"Expected 422 for Yavatmal, got {res.status_code}"
    body = res.json()
    assert "Yavatmal" in str(body)
