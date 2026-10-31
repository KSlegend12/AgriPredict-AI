"""
Comprehensive Automated Tests for Explainable AI (XAI) and Model Integrity.
Tests:
1. Production model and canonical dataset SHA-256 hashes and district safety.
2. SHAP local explanation generation, feature alignment, and exact additivity.
3. Waterfall steps, relative impact percentage, and positive/negative factor sorting.
4. Farmer-friendly non-causal summary and model uncertainty notices.
5. Error resilience: graceful fallback when explainer fails without crashing prediction.
6. Extreme value handling and finite output validation.
7. Global SHAP feature importance endpoint (/api/cotton/xai/global).
8. End-to-end API integration and backward compatibility on /api/cotton/predict.
"""

import os
import hashlib
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.cotton_predictor import (
    cotton_predictor,
    MODEL_PATH,
    DATA_PATH,
    FEATURE_COLS,
    VALID_DISTRICTS,
)
from backend.ml.xai_engine import xai_engine

CANONICAL_DATA_SHA = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PRODUCTION_MODEL_SHA = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# =====================================================================
# 1. ARTIFACT INTEGRITY & DATA SAFETY
# =====================================================================

def test_canonical_dataset_sha256():
    """Verify canonical historical dataset has not been modified."""
    with open(DATA_PATH, "rb") as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    assert actual_sha == CANONICAL_DATA_SHA, (
        f"Canonical dataset hash modified! Expected {CANONICAL_DATA_SHA}, got {actual_sha}"
    )


def test_production_model_sha256():
    """Verify production Gradient Boosting model artifact has not been modified."""
    with open(MODEL_PATH, "rb") as f:
        actual_sha = hashlib.sha256(f.read()).hexdigest()
    assert actual_sha == PRODUCTION_MODEL_SHA, (
        f"Production model hash modified! Expected {PRODUCTION_MODEL_SHA}, got {actual_sha}"
    )


def test_all_seven_districts_preserved():
    """Verify all 7 Vidarbha districts (including Yavatmal) exist in canonical dataset."""
    df = pd.read_csv(DATA_PATH)
    districts = set(df["district"].unique())
    assert set(VALID_DISTRICTS).issubset(districts)
    assert "Yavatmal" in districts
    assert len(districts) == 7


# =====================================================================
# 2. XAI LOCAL EXPLANATION & SHAP ADDITIVITY
# =====================================================================

def test_xai_local_explanation_additivity():
    """Verify SHAP mathematical additivity: Base Value + sum(phi) == Predicted Yield."""
    df = pd.read_csv(DATA_PATH)
    sample_df = df[FEATURE_COLS].iloc[:1]
    predicted_yield = float(cotton_predictor.pipeline.predict(sample_df)[0])

    explanation = xai_engine.generate_local_explanation(
        cotton_predictor.pipeline,
        sample_df,
        predicted_yield,
        cotton_predictor.explainer
    )

    assert explanation["available"] is True
    assert explanation["additivity_verified"] is True
    assert "base_value_kg_ha" in explanation
    assert "waterfall_steps" in explanation

    # Sum contributions
    total_contrib = sum(
        f["contribution_kg_ha"] for f in explanation["top_influential_features"]
    )
    assert isinstance(total_contrib, float)

    # Check waterfall steps start with baseline and end with total
    steps = explanation["waterfall_steps"]
    assert steps[0]["type"] == "baseline"
    assert steps[-1]["type"] == "total"
    assert abs(steps[-1]["contribution_kg_ha"] - predicted_yield) < 0.1


def test_xai_directionality_and_sorting():
    """Verify increasing factors have positive values and decreasing factors have negative values."""
    df = pd.read_csv(DATA_PATH)
    sample_df = df[FEATURE_COLS].iloc[:1]
    predicted_yield = float(cotton_predictor.pipeline.predict(sample_df)[0])

    explanation = xai_engine.generate_local_explanation(
        cotton_predictor.pipeline,
        sample_df,
        predicted_yield,
        cotton_predictor.explainer
    )

    for item in explanation["increasing_factors"]:
        assert item["contribution_kg_ha"] >= 0.0
        assert item["direction"] == "positive"

    for item in explanation["decreasing_factors"]:
        assert item["contribution_kg_ha"] <= 0.0
        assert item["direction"] == "negative"


def test_xai_farmer_narrative_and_disclaimer():
    """Verify summary text and uncertainty notice are present and non-causal."""
    df = pd.read_csv(DATA_PATH)
    sample_df = df[FEATURE_COLS].iloc[:1]
    predicted_yield = float(cotton_predictor.pipeline.predict(sample_df)[0])

    explanation = xai_engine.generate_local_explanation(
        cotton_predictor.pipeline,
        sample_df,
        predicted_yield,
        cotton_predictor.explainer
    )

    summary = explanation["summary_text"]
    assert len(summary) > 20
    assert "kg/ha" in summary

    notice = explanation["uncertainty_notice"]
    assert "106.2 kg/ha" in notice["model_confidence_benchmark"]
    assert "plausible_range_kg_ha" in notice
    assert len(notice["plausible_range_kg_ha"]) == 2
    assert notice["plausible_range_kg_ha"][0] <= predicted_yield <= notice["plausible_range_kg_ha"][1]


# =====================================================================
# 3. ERROR RESILIENCE & FALLBACKS
# =====================================================================

def test_xai_failure_does_not_break_prediction(monkeypatch):
    """Verify that if SHAP explainer fails, prediction still succeeds gracefully."""
    def broken_shap_values(*args, **kwargs):
        raise RuntimeError("Simulated TreeExplainer numerical failure")

    monkeypatch.setattr(cotton_predictor.explainer, "shap_values", broken_shap_values)

    df = pd.read_csv(DATA_PATH)
    sample_row = df[FEATURE_COLS].iloc[0].to_dict()

    result = cotton_predictor.predict(sample_row)

    assert result["status"] == "success"
    assert result["predicted_yield_kg_ha"] > 0
    # Explanation should report unavailable rather than crashing
    assert result["explanation"]["available"] is False
    assert "error" in result["explanation"]


def test_extreme_inputs_yield_non_negative_finite_prediction():
    """Verify predictor bounds yield >= 0 and never returns NaN or infinite values."""
    extreme_inputs = {
        col: 0.0 for col in FEATURE_COLS
    }
    extreme_inputs["district"] = "Akola"
    extreme_inputs["cotton_area_000ha"] = 999.0
    extreme_inputs["tmax_annual_mean_c"] = 55.0
    extreme_inputs["rainfall_annual_mm"] = 0.0

    result = cotton_predictor.predict(extreme_inputs)
    assert result["status"] == "success"
    pred = result["predicted_yield_kg_ha"]
    assert np.isfinite(pred)
    assert pred >= 0.0


# =====================================================================
# 4. API ENDPOINTS & BACKWARD COMPATIBILITY
# =====================================================================

def test_get_global_xai_endpoint(client):
    """Verify /api/cotton/xai/global returns precomputed global feature importance."""
    response = client.get("/api/cotton/xai/global")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["methodology"].startswith("SHAP")
    assert "global_feature_importance" in data
    assert "top_10_features" in data
    assert len(data["top_10_features"]) == 10
    assert "category_summary" in data


def test_cotton_predict_includes_enhanced_xai(client):
    """Verify /api/cotton/predict returns enriched XAI explanation and waterfall steps."""
    payload = {"district": "Wardha", "target_year": 2024}
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "predicted_yield_kg_ha" in data
    assert data["predicted_yield_kg_ha"] > 0

    # XAI block checks
    assert "explanation" in data
    xai = data["explanation"]
    assert xai["available"] is True
    assert "base_value_kg_ha" in xai
    assert "summary_text" in xai
    assert "waterfall_steps" in xai
    assert len(xai["waterfall_steps"]) >= 3
    assert "uncertainty_notice" in xai

    # Backward compatibility checks
    assert "validation_context" in data
    assert "district_historical_context" in data
    assert "global_top_features" in data
    assert "global_shap_importance" in data


# =====================================================================
# 5. SYNTHETIC DATASET & EXPERIMENTAL CANDIDATE ARTIFACT INTEGRITY
# =====================================================================

SYNTH_EXP_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "experiments",
    "synthetic_expansion",
    "data",
    "vidarbha_cotton_model_ready_1997_2024_plus_1000_synthetic.csv",
)

SYNTH_EXP_ARTIFACTS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "experiments",
    "synthetic_expansion",
    "artifacts",
)


def test_synthetic_expansion_dataset_integrity():
    """Verify the 1,194-row expanded dataset structure and partition flags."""
    assert os.path.exists(SYNTH_EXP_DATA_PATH), f"Synthetic dataset not found at {SYNTH_EXP_DATA_PATH}"
    df = pd.read_csv(SYNTH_EXP_DATA_PATH)
    assert len(df) == 1194, f"Expected 1194 rows, got {len(df)}"
    assert "yield_target_kg_ha" in df.columns
    assert "target_review_flag" in df.columns

    synth_rows = df[df["target_review_flag"] == "synthetic_experimental"]
    real_rows = df[df["target_review_flag"] != "synthetic_experimental"]

    assert len(synth_rows) == 1000, f"Expected 1000 synthetic rows, got {len(synth_rows)}"
    assert len(real_rows) == 194, f"Expected 194 real rows, got {len(real_rows)}"

    # Strict leakage check: zero synthetic rows in 2023 or 2024
    assert (synth_rows["year"] >= 2023).sum() == 0, "Synthetic rows found in 2023 or 2024! Leakage detected."


def test_candidate_synthetic_model_artifacts_loadable():
    """Verify experimental candidate model artifact loads and predicts cleanly."""
    import joblib

    candidate_path = os.path.join(SYNTH_EXP_ARTIFACTS_DIR, "GradientBoosting_Synth_100pct.pkl")
    assert os.path.exists(candidate_path), f"Candidate model not found at {candidate_path}"

    candidate_model = joblib.load(candidate_path)
    assert hasattr(candidate_model, "predict")

    # Sample test prediction using 1st row of dataset
    df = pd.read_csv(SYNTH_EXP_DATA_PATH)
    sample = df.iloc[0:1][candidate_model.feature_names_in_]
    pred = candidate_model.predict(sample)[0]
    assert np.isfinite(pred)
    assert pred > 0


def test_controlled_candidate_model_api_prediction(client):
    """Verify API prediction with controlled model_version='candidate_synthetic'."""
    payload = {
        "district": "Wardha",
        "target_year": 2024,
        "model_version": "candidate_synthetic"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["model_version"] == "candidate_synthetic"
    assert data["model_name"] == "GradientBoosting_Synth_100pct"
    assert data["predicted_yield_kg_ha"] > 0
    assert np.isfinite(data["predicted_yield_kg_ha"])
    assert "model_selection_info" in data
    assert data["model_selection_info"]["active_version"] == "candidate_synthetic"

    # Verify validation context shows synthetic expansion performance
    val_ctx = data["validation_context"]
    assert val_ctx["mean_mae_kg_ha"] == 78.5
    assert val_ctx["holdout_mae_kg_ha"] == 198.3


def test_candidate_model_xai_additivity_and_isolation(client):
    """Verify that candidate model XAI explanations match the candidate model, not production."""
    payload = {
        "district": "Nagpur",
        "target_year": 2024,
        "model_version": "candidate_synthetic"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    xai = data["explanation"]
    assert xai["available"] is True
    assert xai["additivity_verified"] is True
    # Base value for candidate model is around ~229.0 kg/ha
    assert 225.0 <= xai["base_value_kg_ha"] <= 235.0
    assert len(xai["waterfall_steps"]) >= 3


def test_candidate_model_metadata_file_completeness():
    """Verify candidate_metadata.json contains all required audit and configuration fields."""
    import json
    metadata_path = os.path.join(SYNTH_EXP_ARTIFACTS_DIR, "candidate_metadata.json")
    assert os.path.exists(metadata_path)

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["model_version"] == "candidate_synthetic"
    assert meta["model_name"] == "GradientBoosting_Synth_100pct"
    assert meta["random_seed"] == 42
    assert "hyperparameters" in meta
    assert len(meta["feature_cols"]) == 36
    assert "dataset_provenance" in meta
    assert meta["dataset_provenance"]["total_dataset_rows"] == 1194
    assert meta["dataset_provenance"]["synthetic_training_rows_1997_2022"] == 1000
    assert meta["validation_metrics_2011_2023"]["Mean_MAE"] < 80.0
    assert meta["holdout_2024_metrics"]["MAE"] < 200.0


# =====================================================================
# 6. OPTIMIZED LEAKAGE-SAFE MODEL & AUDIT TESTS
# =====================================================================

MODEL_OPT_ARTIFACTS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "experiments",
    "model_optimization",
    "artifacts",
)


def test_optimized_candidate_model_artifact_loadable():
    """Verify optimized candidate model artifact loads and predicts cleanly."""
    import joblib

    opt_path = os.path.join(MODEL_OPT_ARTIFACTS_DIR, "GradientBoosting_Optimized_sw005.pkl")
    assert os.path.exists(opt_path), f"Optimized model artifact missing at {opt_path}"

    opt_model = joblib.load(opt_path)
    assert hasattr(opt_model, "predict")

    df = pd.read_csv(SYNTH_EXP_DATA_PATH)
    sample = df.iloc[0:1][opt_model.feature_names_in_]
    pred = opt_model.predict(sample)[0]
    assert np.isfinite(pred)
    assert pred > 0


def test_controlled_optimized_candidate_api_prediction(client):
    """Verify API prediction with controlled model_version='candidate_optimized'."""
    payload = {
        "district": "Wardha",
        "target_year": 2024,
        "model_version": "candidate_optimized"
    }
    response = client.post("/api/cotton/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["model_version"] == "candidate_optimized"
    assert data["model_name"] == "GradientBoosting_Optimized_sw005"
    assert data["predicted_yield_kg_ha"] > 0
    assert np.isfinite(data["predicted_yield_kg_ha"])

    # XAI check for optimized candidate
    xai = data["explanation"]
    assert xai["available"] is True
    assert xai["additivity_verified"] is True
    # Base value for optimized model is around ~230.3 kg/ha
    assert 225.0 <= xai["base_value_kg_ha"] <= 235.0


def test_anchor_leakage_discovery_validation():
    """Verify that synthetic dataset contains anchor pairs and max_anchor_year spans through 2023."""
    import re
    df = pd.read_csv(SYNTH_EXP_DATA_PATH)
    synth_df = df[df["target_review_flag"] == "synthetic_experimental"]

    def parse_anchors(note):
        m = re.search(r"Anchors:\s*(\w+)\s*(\d{4})\s*and\s*(\d{4})", str(note))
        if m:
            return int(m.group(2)), int(m.group(3))
        return None, None

    synth_df = synth_df.copy()
    parsed = synth_df["target_note"].apply(parse_anchors)
    synth_df["anchor_y1"] = [p[0] for p in parsed]
    synth_df["anchor_y2"] = [p[1] for p in parsed]
    synth_df["max_anchor_year"] = synth_df[["anchor_y1", "anchor_y2"]].max(axis=1)

    # Synthetic rows labeled year 2022 contain anchor 2023
    leaked_into_2023_val = synth_df[(synth_df["year"] < 2023) & (synth_df["max_anchor_year"] >= 2023)]
    assert len(leaked_into_2023_val) == 32, f"Expected 32 anchor-leaked rows, found {len(leaked_into_2023_val)}"



