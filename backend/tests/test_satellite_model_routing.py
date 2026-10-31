"""
Test suite for opt-in satellite dual-model API routing in AgriPredict-AI.
Verifies production invariance, explicit model routing, input validation,
unsupported year rejection, SHAP additivity, and rejection of unknown model versions.
"""

import hashlib
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import CANONICAL_COTTON_DATASET_PATH
from backend.ml.cotton_predictor import (
    cotton_predictor,
    FEATURE_COLS,
    SATELLITE_SMAP_FEATURES,
    SATELLITE_FEATURE_COLS,
    MODEL_PATH,
    SATELLITE_MODEL_PATH,
    SATELLITE_METADATA_PATH,
)
from backend.services.cotton_input_builder import cotton_input_builder

client = TestClient(app)

CANONICAL_DATASET_SHA256 = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PRODUCTION_MODEL_SHA256 = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"


def test_production_invariants_preserved():
    """Ensure canonical dataset and production model SHA-256 remain completely unchanged."""
    with open(CANONICAL_COTTON_DATASET_PATH, "rb") as f:
        data_hash = hashlib.sha256(f.read()).hexdigest()
    assert data_hash == CANONICAL_DATASET_SHA256, "Canonical dataset was modified!"

    with open(MODEL_PATH, "rb") as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()
    assert model_hash == PRODUCTION_MODEL_SHA256, "Production model was modified!"


def test_production_model_remains_default():
    """When model_version is omitted, the production model must be served by default."""
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["model_version"] == "production"
    assert data["satellite_features_used"] is False
    assert data["model_name"] == "GradientBoosting"
    assert data["model_selection_info"]["active_version"] == "production"
    assert data["model_selection_info"]["satellite_features_used"] is False


def test_explicit_production_model_selection():
    """Explicitly requesting model_version='production' routes to production model."""
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024,
        "model_version": "production"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["model_version"] == "production"
    assert data["satellite_features_used"] is False


def test_explicit_satellite_smap_candidate_selection_2024():
    """Explicitly requesting candidate_satellite_smap for valid year (2024) succeeds."""
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024,
        "model_version": "candidate_satellite_smap"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "success"
    assert data["model_version"] == "candidate_satellite_smap"
    assert data["satellite_features_used"] is True
    assert "Satellite_SMAP" in data["model_name"]
    assert data["model_selection_info"]["active_version"] == "candidate_satellite_smap"
    assert data["model_selection_info"]["satellite_features_used"] is True
    assert data["predicted_yield_kg_ha"] > 0


def test_satellite_model_unsupported_historical_year_rejected():
    """Pre-satellite years (e.g., 2015) must be rejected with 422 and clear explanation (no silent fallback)."""
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2015,
        "model_version": "candidate_satellite_smap"
    })
    assert res.status_code == 422, "Pre-satellite year should be rejected"
    detail = res.json().get("detail", "")
    assert "2018–2024" in detail or "verified satellite" in detail.lower()
    # Crucial: verify it did NOT silently succeed by falling back to production
    assert "status" not in res.json() or res.json()["status"] != "success"


def test_unknown_model_version_rejected():
    """An unknown model version must be rejected with a 422 validation error."""
    res = client.post("/api/cotton/predict", json={
        "district": "Akola",
        "target_year": 2024,
        "model_version": "unsupported_super_model_v9"
    })
    assert res.status_code == 422
    detail = res.json().get("detail", "")
    assert "Unknown model_version" in detail or "Valid options" in detail


def test_satellite_missing_features_rejected_without_silent_fabrication():
    """Direct predictor call with missing satellite features must fail, not fabricate measurements."""
    # Build standard 36-feature row
    built = cotton_input_builder.build("Akola", 2024, model_version="production")
    raw_feats = built["features"].copy()
    # Explicitly attempt candidate_satellite_smap without supplying the 6 SMAP features
    res = cotton_predictor.predict(raw_feats, model_version="candidate_satellite_smap")
    assert res["status"] == "error"
    assert "Missing required NASA SMAP" in res["message"]


def test_satellite_candidate_exact_feature_schema():
    """Verify exact 42-feature schema order for satellite model."""
    built = cotton_input_builder.build("Akola", 2024, model_version="candidate_satellite_smap")
    features = built["features"]
    assert len(features) == 42, f"Expected 42 features, got {len(features)}"
    for col in SATELLITE_SMAP_FEATURES:
        assert col in features
        assert features[col] is not None
        assert not (isinstance(features[col], float) and features[col] != features[col])
        assert 0.0 <= features[col] <= 1.0, f"SMAP volumetric water content out of physical bounds: {features[col]}"


def test_satellite_candidate_shap_additivity():
    """Verify that SHAP TreeExplainer produces exact mathematical additivity for satellite model."""
    built = cotton_input_builder.build("Wardha", 2024, model_version="candidate_satellite_smap")
    res = cotton_predictor.predict(built["features"], model_version="candidate_satellite_smap")
    assert res["status"] == "success"
    explanation = res["explanation"]
    assert explanation["available"] is True
    assert explanation["additivity_verified"] is True
    assert "waterfall_steps" in explanation
    steps = explanation["waterfall_steps"]
    assert steps[0]["type"] == "baseline"
    assert steps[-1]["type"] == "total"
    assert abs(steps[-1]["contribution_kg_ha"] - res["predicted_yield_kg_ha"]) < 0.1


def test_all_seven_districts_predictable_with_satellite_candidate_2024():
    """Ensure all 7 Vidarbha districts successfully predict in 2024 using candidate_satellite_smap."""
    for dist in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]:
        res = client.post("/api/cotton/predict", json={
            "district": dist,
            "target_year": 2024,
            "model_version": "candidate_satellite_smap"
        })
        assert res.status_code == 200, f"Failed for {dist}: {res.text}"
        data = res.json()
        assert data["satellite_features_used"] is True
        assert data["predicted_yield_kg_ha"] > 0
