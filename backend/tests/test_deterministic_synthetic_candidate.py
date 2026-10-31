import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import joblib

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CANONICAL_PATH = REPO_ROOT / "data/vidarbha_cotton_model_ready_1997_2024.csv"
PROD_MODEL_PATH = REPO_ROOT / "backend/ml/artifacts/final_model.pkl"
CANDIDATE_PATH = REPO_ROOT / "backend/ml/experiments/performance_optimization/artifacts/Ridge_Delta_Biophysical_Synth_Deterministic.pkl"
METADATA_PATH = REPO_ROOT / "backend/ml/experiments/performance_optimization/artifacts/biophysical_synth_deterministic_metadata.json"

EXPECTED_CANONICAL_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
EXPECTED_PROD_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

from backend.ml.cotton_predictor import DELTA_ROLLING_FEATURE_COLS, VALID_DISTRICTS
from backend.services.cotton_input_builder import cotton_input_builder
from backend.ml.xai_engine import xai_engine

def test_cryptographic_invariants_preserved():
    h_csv = hashlib.sha256(CANONICAL_PATH.read_bytes()).hexdigest()
    h_model = hashlib.sha256(PROD_MODEL_PATH.read_bytes()).hexdigest()
    assert h_csv == EXPECTED_CANONICAL_HASH, f"Canonical dataset modified: {h_csv}"
    assert h_model == EXPECTED_PROD_MODEL_HASH, f"Production model modified: {h_model}"

def test_deterministic_candidate_artifact_exists_and_schema():
    assert CANDIDATE_PATH.exists(), f"Candidate artifact missing: {CANDIDATE_PATH}"
    assert METADATA_PATH.exists(), f"Candidate metadata missing: {METADATA_PATH}"
    
    with open(METADATA_PATH, "r") as f:
        meta = json.load(f)
    
    assert meta["model_name"] == "Ridge_Delta_Biophysical_Synth_Deterministic"
    assert meta["feature_count"] == len(DELTA_ROLLING_FEATURE_COLS)
    assert meta["features"] == DELTA_ROLLING_FEATURE_COLS

def test_deterministic_reproduction_of_benchmark_predictions():
    pipe = joblib.load(CANDIDATE_PATH)
    with open(METADATA_PATH, "r") as f:
        meta = json.load(f)
    
    benchmark_preds = meta["benchmark_2024_holdout_predictions"]
    
    df_canonical = pd.read_csv(CANONICAL_PATH)
    h2024 = df_canonical[df_canonical["year"] == 2024].copy()
    
    # Compute agronomic features
    h2024["diurnal_range_kharif"] = h2024["tmax_kharif_mean_c"] - h2024["tmin_kharif_mean_c"]
    h2024["rain_intensity_kharif"] = h2024["rainfall_kharif_mm"] / np.maximum(h2024["rainy_days_kharif"], 1.0)
    h2024["dry_heat_compound"] = h2024["max_dry_spell_kharif_days"] * h2024["tmax_hot_days_ge35_kharif"]
    h2024["single_day_deluge_ratio"] = h2024["rainfall_max_1day_kharif_mm"] / np.maximum(h2024["rainfall_kharif_mm"], 1.0)
    h2024["yield_momentum"] = h2024["previous_year_yield_kg_ha"] - h2024["previous_2year_yield_kg_ha"]
    h2024["yield_ratio_to_rolling3"] = h2024["previous_year_yield_kg_ha"] / np.maximum(h2024["rolling_3yr_yield_mean_kg_ha"], 1.0)
    
    train_history = df_canonical[df_canonical["year"] < 2024]
    anchor = h2024["rolling_3yr_yield_mean_kg_ha"].fillna(train_history["yield_target_kg_ha"].median()).values
    
    pred_delta = pipe.predict(h2024[DELTA_ROLLING_FEATURE_COLS])
    reloaded_preds = np.maximum(0.0, anchor + pred_delta)
    
    for i, (_, r) in enumerate(h2024.iterrows()):
        d = r["district"]
        expected_p = benchmark_preds[d]
        actual_p = reloaded_preds[i]
        assert abs(actual_p - expected_p) < 1e-4, f"District {d}: reloaded {actual_p:.4f} != expected {expected_p:.4f}"

def test_deterministic_candidate_shap_additivity():
    pipe = joblib.load(CANDIDATE_PATH)
    
    for dist in VALID_DISTRICTS:
        built = cotton_input_builder.build(dist, 2024, model_version="candidate_delta_rolling")
        X_df = pd.DataFrame([built["features"]])[DELTA_ROLLING_FEATURE_COLS]
        anchor = float(built["features"]["rolling_3yr_yield_mean_kg_ha"])
        
        delta_p = float(pipe.predict(X_df)[0])
        final_p = max(0.0, anchor + delta_p)
        
        exp = xai_engine.generate_local_explanation(
            pipeline=pipe,
            X_df=X_df,
            predicted_yield=final_p,
            anchor_value=anchor
        )
        assert exp["additivity_verified"] is True
        total_step = next(s for s in exp["waterfall_steps"] if s["type"] == "total")
        assert abs(final_p - total_step["contribution_kg_ha"]) < 0.01
