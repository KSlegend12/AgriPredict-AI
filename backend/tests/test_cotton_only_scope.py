"""
Automated Scope Regression & Integrity Test Suite for AgriPredict-AI.

Verifies:
1. Cryptographic SHA-256 integrity of protected historical dataset and production model artifact.
2. Strict 6-district Vidarbha geographic boundary (Yavatmal excluded by design).
3. Strict Cotton-only crop scope enforcement across all prediction and advisory endpoints.
4. Non-cotton crop rejection (Tomato, Onion, Sugarcane, Soybean, Wheat, etc.) with HTTP 422.
5. Yavatmal exclusion verification:
   - Rejected with HTTP 422 in cotton prediction requests.
   - Excluded from supported Vidarbha districts configuration and endpoints.
6. Field observation and outcome comparison schemas reject non-cotton crops.
"""

import hashlib
import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import SUPPORTED_VIDARBHA_DISTRICTS, ALLOWED_CROPS

CANONICAL_DATASET_PATH = os.path.join("data", "vidarbha_cotton_model_ready_1997_2024.csv")
CANONICAL_DATASET_SHA256 = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"

FINAL_MODEL_PATH = os.path.join("backend", "ml", "artifacts", "final_model.pkl")
FINAL_MODEL_SHA256 = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

EXPECTED_6_DISTRICTS = {
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim",
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# =====================================================================
# 1. PROTECTED ASSET CRYPTOGRAPHIC INTEGRITY
# =====================================================================

def test_canonical_dataset_integrity():
    """Verify data/vidarbha_cotton_model_ready_1997_2024.csv is untouched and matches canonical SHA-256."""
    assert os.path.isfile(CANONICAL_DATASET_PATH), f"Dataset missing at {CANONICAL_DATASET_PATH}"
    with open(CANONICAL_DATASET_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == CANONICAL_DATASET_SHA256, (
        f"Dataset hash mismatch! Expected {CANONICAL_DATASET_SHA256}, got {file_hash}"
    )


def test_final_model_artifact_integrity():
    """Verify backend/ml/artifacts/final_model.pkl is untouched and matches canonical SHA-256."""
    assert os.path.isfile(FINAL_MODEL_PATH), f"Model missing at {FINAL_MODEL_PATH}"
    with open(FINAL_MODEL_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == FINAL_MODEL_SHA256, (
        f"Model hash mismatch! Expected {FINAL_MODEL_SHA256}, got {file_hash}"
    )


# =====================================================================
# 2. GEOGRAPHIC SCOPE ENFORCEMENT (6 VIDARBHA DISTRICTS, YAVATMAL EXCLUDED)
# =====================================================================

def test_config_supported_districts():
    """Verify configuration exposes exactly the 6 Vidarbha research districts (Yavatmal excluded)."""
    assert set(SUPPORTED_VIDARBHA_DISTRICTS) == EXPECTED_6_DISTRICTS
    assert len(SUPPORTED_VIDARBHA_DISTRICTS) == 6
    assert "Yavatmal" not in SUPPORTED_VIDARBHA_DISTRICTS


def test_cotton_districts_endpoint(client):
    """Verify /api/cotton/districts returns exactly the 6 Vidarbha research districts."""
    response = client.get("/api/cotton/districts")
    assert response.status_code == 200
    data = response.json()
    assert "districts" in data
    districts = [d["district"] for d in data["districts"]]
    assert set(districts) == EXPECTED_6_DISTRICTS
    assert len(districts) == 6
    assert "Yavatmal" not in districts


def test_districts_endpoint_allowed_crops(client):
    """Verify /api/districts returns allowed_crops strictly as ['Cotton'] and 6 Vidarbha districts."""
    response = client.get("/api/districts")
    assert response.status_code == 200
    data = response.json()
    assert data["allowed_crops"] == ["Cotton"]
    assert "vidarbha_scope_districts" in data
    assert set(data["vidarbha_scope_districts"]) == EXPECTED_6_DISTRICTS
    assert "Yavatmal" not in data["vidarbha_scope_districts"]


# =====================================================================
# 3. NON-COTTON REJECTION IN YIELD PREDICTION
# =====================================================================

@pytest.mark.parametrize("invalid_crop", [
    "Tomato",
    "Onion",
    "Sugarcane",
    "Soybean",
    "Wheat",
    "Gram",
    "Rice",
    "Maize",
])
def test_yield_predict_rejects_non_cotton_crops(client, invalid_crop):
    """Verify /api/yield/predict explicitly rejects non-cotton crops with HTTP 422."""
    payload = {
        "crop": invalid_crop,
        "district": "Nagpur",
        "season": "Kharif",
        "rainfall": 850.0,
        "temperature": 28.5,
        "humidity": 70.0,
        "nitrogen": 120.0,
        "phosphorus": 45.0,
        "potassium": 50.0,
        "soil_ph": 7.2,
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 422
    assert "Cotton" in response.text or "not supported" in response.text


def test_yield_predict_accepts_cotton(client):
    """Verify /api/yield/predict accepts Cotton."""
    payload = {
        "crop": "Cotton",
        "district": "Nagpur",
        "season": "Kharif",
        "rainfall": 850.0,
        "temperature": 28.5,
        "humidity": 70.0,
        "nitrogen": 120.0,
        "phosphorus": 45.0,
        "potassium": 50.0,
        "soil_ph": 7.2,
    }
    response = client.post("/api/yield/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "Cotton"
    assert data["predicted_yield_ha"] > 0


# =====================================================================
# 4. YAVATMAL DISTRICT EXCLUSION VERIFICATION
# =====================================================================

def test_yavatmal_rejected_from_cotton_predict(client):
    """Verify Yavatmal is strictly rejected with HTTP 422 from cotton yield prediction."""
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": "candidate_six_district_thermal",
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422
    assert "Yavatmal" in response.text or "not supported" in response.text.lower() or "input should be" in response.text.lower()


def test_yavatmal_rejected_from_cotton_input(client):
    """Verify verified feature builder rejects Yavatmal with HTTP 422."""
    response = client.get("/api/cotton/input/Yavatmal/2024")
    assert response.status_code == 422
    assert "Yavatmal" in response.text or "not supported" in response.text.lower()


# =====================================================================
# 5. FIELD OBSERVATION & OUTCOME SCHEMAS REJECT NON-COTTON
# =====================================================================

def test_field_observation_rejects_non_cotton(client):
    """Verify field observation endpoint rejects non-cotton crop observations."""
    payload = {
        "district": "Nagpur",
        "taluka": "Katol",
        "crop": "Tomato",
        "observation_date": "2026-10-15",
        "growth_stage": "Flowering",
        "plant_height_cm": 65.0,
    }
    response = client.post("/api/field-observations/record", json=payload)
    assert response.status_code == 422


def test_outcome_comparison_rejects_non_cotton(client):
    """Verify outcome comparison endpoint rejects non-cotton crops."""
    payload = {
        "district": "Nagpur",
        "crop": "Soybean",
        "year": 2024,
        "observed_yield": 450.0,
    }
    response = client.post("/api/outcomes/compare", json=payload)
    assert response.status_code == 422
