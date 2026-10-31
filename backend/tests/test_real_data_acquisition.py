"""
Pytest integration suite for the Real Agricultural Data Acquisition Pipeline.
"""

import os
import json
import hashlib
import pytest
import pandas as pd
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_ACQ_DIR = os.path.join(_REPO_ROOT, "backend", "ml", "experiments", "performance_optimization", "real_data_acquisition")

CANONICAL_PATH = os.path.join(_REPO_ROOT, "data", "vidarbha_cotton_model_ready_1997_2024.csv")
MODEL_PATH = os.path.join(_REPO_ROOT, "backend", "ml", "artifacts", "final_model.pkl")

EXPECTED_CANONICAL_HASH = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
EXPECTED_MODEL_HASH = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest().lower()


def test_canonical_and_production_invariants_preserved():
    assert sha256_file(CANONICAL_PATH) == EXPECTED_CANONICAL_HASH
    assert sha256_file(MODEL_PATH) == EXPECTED_MODEL_HASH


def test_source_manifest_structure_and_reachability():
    manifest_path = os.path.join(_ACQ_DIR, "source_manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "sources" in manifest
    assert len(manifest["sources"]) == 6

    for src in manifest["sources"]:
        assert "source_id" in src
        assert "official_portal" in src or "icrisat_portal" in src
        assert "reachability_verified" in src
        assert "missingness_percentage" in src


def test_forecast_timing_isolation():
    pre_path = os.path.join(_ACQ_DIR, "data", "pre_season_research_dataset.csv")
    in_path = os.path.join(_ACQ_DIR, "data", "in_season_research_dataset.csv")

    assert os.path.exists(pre_path)
    assert os.path.exists(in_path)

    df_pre = pd.read_csv(pre_path)
    df_in = pd.read_csv(in_path)

    assert len(df_pre) == 194
    assert len(df_in) == 194

    forbidden_in_pre = [
        "rainfall_kharif_mm",
        "rainfall_monsoon_mm",
        "rainy_days_kharif",
        "heavy_rain_days_kharif",
        "rainfall_max_1day_kharif_mm",
        "max_5day_rain_kharif_mm",
        "max_dry_spell_kharif_days",
        "tmax_kharif_mean_c",
        "tmax_hot_days_ge35_kharif",
        "tmin_kharif_mean_c",
        "sm_rootzone_kharif_mean",
        "sm_surface_kharif_mean"
    ]
    for col in forbidden_in_pre:
        assert col not in df_pre.columns, f"Leaked in-season variable {col} into pre-season dataset"


def test_temporal_evaluation_artifacts_exist():
    results_dir = os.path.join(_ACQ_DIR, "results")
    assert os.path.exists(os.path.join(results_dir, "temporal_cv_summary.csv"))
    assert os.path.exists(os.path.join(results_dir, "temporal_2024_holdout_summary.csv"))
    assert os.path.exists(os.path.join(results_dir, "temporal_cv_regime_summary.csv"))

    df_cv = pd.read_csv(os.path.join(results_dir, "temporal_cv_summary.csv"))
    assert len(df_cv) == 5
    assert "Ridge_Delta_Rolling_Agronomic" in df_cv["model"].values
    assert "Production_GB_Benchmark" in df_cv["model"].values
    assert "PreSeason_ForecastOrigin_Ridge" in df_cv["model"].values
