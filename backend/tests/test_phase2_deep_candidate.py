"""
Tests for Phase 2 Deep Scientific Candidate Model:
Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh
"""
import pytest
import json
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import shap

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXP_DIR = REPO_ROOT / "backend/ml/experiments/phase2_deep_scientific_optimization_2026/artifacts"
MODEL_PATH = EXP_DIR / "Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh.pkl"
META_PATH = EXP_DIR / "metadata_Decoupled_Agronomic_Ridge_Deficit_HeatThresh_a75.json"
DATA_PATH = REPO_ROOT / "backend/ml/experiments/six_district_optimization/data/vidarbha_cotton_six_districts_1997_2024.csv"

def test_phase2_candidate_artifacts_exist():
    assert MODEL_PATH.exists(), f"Model artifact missing at {MODEL_PATH}"
    assert META_PATH.exists(), f"Metadata missing at {META_PATH}"

def test_phase2_candidate_metadata_schema():
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["model_name"] == "Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh"
    assert meta["alpha"] == 75.0
    assert "performance_13fold_cv" in meta
    assert meta["performance_13fold_cv"]["cv_mae_kg_ha"] <= 102.65
    assert meta["performance_13fold_cv"]["cv_rmse_kg_ha"] <= 136.05
    assert meta["performance_13fold_cv"]["cv_r2"] >= 0.2530

def test_phase2_candidate_inference_and_shap():
    pipe = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    
    # Engineer test features
    df["extreme_heat_ratio"] = df["tmax_hot_days_ge35_kharif"] / 120.0
    df["diurnal_range_kharif"] = df["tmax_kharif_mean_c"] - df["tmin_kharif_mean_c"]
    df["excess_rain_kharif"] = np.maximum(0.0, df["rainfall_kharif_mm"] - 800.0) / 100.0
    df["continuous_wetness_risk"] = (df["rainy_days_kharif"] / 120.0) / (df["max_dry_spell_kharif_days"] + 1.0)
    df["rain_deficit_kharif"] = np.maximum(0.0, 750.0 - df["rainfall_kharif_mm"]) / 100.0
    df["hot_days_thresh10"] = np.maximum(0.0, df["tmax_hot_days_ge35_kharif"] - 10.0) / 10.0

    test_2024 = df[df["year"] == 2024].copy().reset_index(drop=True)
    assert len(test_2024) == 6

    # Test inference
    pred_delta = pipe.predict(test_2024)
    anchor = test_2024["rolling_3yr_yield_mean_kg_ha"].values
    final_preds = np.maximum(10.0, anchor + pred_delta)

    assert len(final_preds) == 6
    assert np.all(final_preds > 0), "All predictions must be positive yield"

    # Test SHAP LinearExplainer additivity
    prep = pipe.named_steps["prep"]
    ridge = pipe.named_steps["model"]
    background = prep.transform(df[df["year"] <= 2023].iloc[:100])
    explainer = shap.LinearExplainer(ridge, background)
    
    X_test = prep.transform(test_2024.iloc[0:1])
    shap_vals = explainer.shap_values(X_test)
    base_val = explainer.expected_value
    reconstructed_delta = base_val + np.sum(shap_vals)
    expected_delta = ridge.predict(X_test)[0]

    assert abs(reconstructed_delta - expected_delta) < 1e-5, "SHAP additivity violated"
