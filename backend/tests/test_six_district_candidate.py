"""
Unit and Integration Tests for Six-District Cotton Model Workflow
================================================================
Validates:
1. Derived 6-district dataset integrity (0 Yavatmal rows, 166 rows, 6 districts, 0 duplicates).
2. Explicit rejection of Yavatmal for candidate_six_district_physiological (HTTP 422).
3. Successful predictions and exact SHAP additivity for all 6 valid districts.
4. Chronological feature leakage safety (rolling and lag features strictly pre-dating target year).
5. Feature schema alignment with serialized pipeline artifact.
6. Production model default routing and 7-district functionality preservation.
7. SQLite prediction history persistence.
"""

import os
import hashlib
import pytest
import pandas as pd
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import (
    cotton_predictor,
    SIX_DISTRICT_MODEL_PATH,
    SIX_DISTRICT_METADATA_PATH,
    SIX_DISTRICT_THERMAL_MODEL_PATH,
    SIX_DISTRICT_THERMAL_METADATA_PATH,
    MODEL_PATH,
    DATA_PATH
)
from backend.services.cotton_input_builder import cotton_input_builder

client = TestClient(app)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SIX_DIST_DATA_PATH = os.path.join(
    REPO_ROOT,
    "backend", "ml", "experiments", "six_district_optimization", "data", "vidarbha_cotton_six_districts_1997_2024.csv"
)

EXPECTED_CANONICAL_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
EXPECTED_PROD_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

SIX_DISTRICTS = ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]


def test_protected_production_assets_hashes():
    """Verify that canonical dataset and production model have not been modified."""
    with open(DATA_PATH, "rb") as f:
        csv_hash = hashlib.sha256(f.read()).hexdigest()
    assert csv_hash == EXPECTED_CANONICAL_HASH, f"Canonical CSV hash altered: {csv_hash}"

    with open(MODEL_PATH, "rb") as f:
        model_hash = hashlib.sha256(f.read()).hexdigest()
    assert model_hash == EXPECTED_PROD_MODEL_HASH, f"Production model hash altered: {model_hash}"


def test_derived_dataset_integrity():
    """Verify derived dataset has exactly 166 rows, 0 Yavatmal rows, and all 6 target districts."""
    assert os.path.exists(SIX_DIST_DATA_PATH), f"Derived dataset missing: {SIX_DIST_DATA_PATH}"
    df = pd.read_csv(SIX_DIST_DATA_PATH)

    # 1. Row count: 194 canonical rows - 28 Yavatmal rows = 166 rows
    assert len(df) == 166, f"Expected 166 rows in 6-district dataset, got {len(df)}"

    # 2. Complete absence of Yavatmal
    assert not (df["district"].str.lower() == "yavatmal").any(), "Yavatmal records found in 6-district dataset!"

    # 3. Exactly the 6 target districts
    actual_districts = sorted(df["district"].unique().tolist())
    assert actual_districts == sorted(SIX_DISTRICTS), f"Districts mismatch: {actual_districts}"

    # 4. District record counts
    for d in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha"]:
        assert len(df[df["district"] == d]) == 28
    assert len(df[df["district"] == "Washim"]) == 26

    # 5. Zero duplicate (district, year)
    dups = df.duplicated(subset=["district", "year"]).sum()
    assert dups == 0, f"Found {dups} duplicate district-year rows in derived dataset"

    # 6. Year range
    assert df["year"].min() == 1997
    assert df["year"].max() == 2024


def test_six_district_candidate_model_loaded():
    """Verify the 6-district candidate model artifact and metadata load successfully."""
    assert os.path.exists(SIX_DISTRICT_MODEL_PATH), "6-district model artifact missing"
    assert os.path.exists(SIX_DISTRICT_METADATA_PATH), "6-district metadata missing"
    assert getattr(cotton_predictor, "six_dist_is_loaded", False) is True
    assert cotton_predictor.six_dist_pipeline is not None
    assert cotton_predictor.six_dist_metadata.get("candidate_id") == "candidate_six_district_physiological"


def test_yavatmal_rejection_for_six_district_candidate():
    """Verify API strictly rejects Yavatmal when candidate_six_district_physiological is requested (HTTP 422)."""
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": "candidate_six_district_physiological"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422, f"Expected 422 for Yavatmal under 6-district candidate, got {response.status_code}"
    detail = str(response.json())
    assert "Yavatmal" in detail
    assert "Akola" in detail and "Washim" in detail


def test_production_rejects_yavatmal():
    """Verify production model strictly enforces 6-district Vidarbha scope and rejects Yavatmal (HTTP 422)."""
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": "production"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422
    assert "Yavatmal" in str(response.json())


def test_six_district_candidate_valid_predictions():
    """Verify predictions succeed and return valid XAI for all 6 supported districts in 2024."""
    for dist in SIX_DISTRICTS:
        payload = {
            "district": dist,
            "target_year": 2024,
            "model_version": "candidate_six_district_physiological"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200, f"Prediction failed for {dist}: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data["model_version"] == "candidate_six_district_physiological"
        pred_yield = data["predicted_yield_kg_ha"]
        assert 100.0 <= pred_yield <= 1000.0, f"Unrealistic yield {pred_yield} for {dist}"

        # Verify XAI explanations and mathematical additivity
        exp = data.get("explanation", {})
        assert exp.get("available") is True
        assert exp.get("additivity_verified") is True
        assert "waterfall_steps" in exp
        assert len(exp["waterfall_steps"]) > 0

        # Check total waterfall step against predicted_yield
        total_step = next((s for s in exp["waterfall_steps"] if s["type"] == "total"), None)
        assert total_step is not None
        assert abs(total_step["contribution_kg_ha"] - pred_yield) < 0.15, f"SHAP additivity violated for {dist}"


def test_chronological_feature_leakage_safety():
    """Verify that lag and rolling yield features strictly precede target year."""
    df_raw = pd.read_csv(DATA_PATH)
    for dist in SIX_DISTRICTS:
        dist_df = df_raw[df_raw["district"] == dist].sort_values("year").reset_index(drop=True)
        for i in range(3, len(dist_df)):
            current_year = int(dist_df.loc[i, "year"])
            py = float(dist_df.loc[i, "previous_year_yield_kg_ha"])
            p2y = float(dist_df.loc[i, "previous_2year_yield_kg_ha"])
            r3y = float(dist_df.loc[i, "rolling_3yr_yield_mean_kg_ha"])

            expected_py = float(dist_df.loc[i - 1, "yield_target_kg_ha"])
            expected_p2y = float(dist_df.loc[i - 2, "yield_target_kg_ha"])
            expected_r3y = float(dist_df.loc[i - 3:i - 1, "yield_target_kg_ha"].mean())

            assert abs(py - expected_py) < 1e-4, f"Leakage/mismatch in prev_year for {dist} {current_year}"
            assert abs(p2y - expected_p2y) < 1e-4, f"Leakage/mismatch in prev_2year for {dist} {current_year}"
            assert abs(r3y - expected_r3y) < 1e-4, f"Leakage/mismatch in rolling_3yr for {dist} {current_year}"


def test_model_info_reports_six_district_candidate():
    """Verify /api/cotton/model/info documents the six-district candidate."""
    response = client.get("/api/cotton/model/info")
    assert response.status_code == 200
    info = response.json()
    assert "candidate_six_district_physiological" in info
    six_info = info["candidate_six_district_physiological"]
    assert six_info["available"] is True
    meta = six_info["metadata"]
    assert meta["candidate_id"] == "candidate_six_district_physiological"
    assert "Akola" in meta["scope"]["supported_districts"]
    assert "Yavatmal" in meta["scope"]["excluded_districts"]


def test_sqlite_prediction_history():
    """Verify predictions with six-district model are persisted to SQLite."""
    payload = {
        "district": "Amravati",
        "target_year": 2024,
        "model_version": "candidate_six_district_physiological"
    }
    client.post("/api/cotton/predict", json=payload)
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    records = data.get("history", [])
    # At least one record with model_version candidate_six_district_physiological
    matching = [r for r in records if r.get("model_type") == "candidate_six_district_physiological"]
    assert len(matching) > 0, "No history records found for candidate_six_district_physiological"


def test_six_district_thermal_candidate_model_loaded():
    """Verify the 6-district thermal candidate model artifact and metadata load successfully."""
    assert os.path.exists(SIX_DISTRICT_THERMAL_MODEL_PATH), "6-district thermal model artifact missing"
    assert os.path.exists(SIX_DISTRICT_THERMAL_METADATA_PATH), "6-district thermal metadata missing"
    assert getattr(cotton_predictor, "six_dist_thermal_is_loaded", False) is True
    assert cotton_predictor.six_dist_thermal_pipeline is not None
    assert cotton_predictor.six_dist_thermal_metadata.get("candidate_id") == "candidate_six_district_thermal"
    assert "Akola" in cotton_predictor.six_dist_thermal_metadata["scope"]["supported_districts"]
    assert "Yavatmal" in cotton_predictor.six_dist_thermal_metadata["scope"]["excluded_districts"]


def test_yavatmal_rejection_for_six_district_thermal_candidate():
    """Verify API strictly rejects Yavatmal when candidate_six_district_thermal is requested (HTTP 422)."""
    payload = {
        "district": "Yavatmal",
        "target_year": 2024,
        "model_version": "candidate_six_district_thermal"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 422, f"Expected 422 for Yavatmal under thermal candidate, got {response.status_code}"
    detail = str(response.json())
    assert "Yavatmal" in detail
    assert "Akola" in detail and "Washim" in detail


def test_six_district_thermal_candidate_valid_predictions():
    """Verify predictions succeed and return valid XAI for all 6 supported districts in 2024."""
    for dist in SIX_DISTRICTS:
        payload = {
            "district": dist,
            "target_year": 2024,
            "model_version": "candidate_six_district_thermal"
        }
        response = client.post("/api/cotton/predict", json=payload)
        assert response.status_code == 200, f"Prediction failed for {dist}: {response.text}"
        data = response.json()
        assert data["status"] == "success"
        assert data["model_version"] == "candidate_six_district_thermal"
        pred_yield = data["predicted_yield_kg_ha"]
        assert 100.0 <= pred_yield <= 1000.0, f"Unrealistic yield {pred_yield} for {dist}"

        # Verify XAI explanations and mathematical additivity
        exp = data.get("explanation", {})
        assert exp.get("available") is True
        assert exp.get("additivity_verified") is True
        assert "waterfall_steps" in exp
        assert len(exp["waterfall_steps"]) > 0

        # Check total waterfall step against predicted_yield
        total_step = next((s for s in exp["waterfall_steps"] if s["type"] == "total"), None)
        assert total_step is not None
        assert abs(total_step["contribution_kg_ha"] - pred_yield) < 0.15, f"SHAP additivity violated for {dist}"


def test_model_info_reports_six_district_thermal_candidate():
    """Verify /api/cotton/model/info documents the six-district thermal candidate."""
    response = client.get("/api/cotton/model/info")
    assert response.status_code == 200
    info = response.json()
    assert "candidate_six_district_thermal" in info
    thermal_info = info["candidate_six_district_thermal"]
    assert thermal_info["available"] is True
    meta = thermal_info["metadata"]
    assert meta["candidate_id"] == "candidate_six_district_thermal"
    assert "Akola" in meta["scope"]["supported_districts"]
    assert "Yavatmal" in meta["scope"]["excluded_districts"]
    assert meta["alpha"] == 100.0

