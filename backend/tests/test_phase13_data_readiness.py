"""
Phase 13 Automated Test Suite: Authentic Agricultural Dataset Acquisition & Multi-Crop Readiness.

Covers:
1. Authentic vs synthetic dataset classification in permanent provenance registry.
2. Authentic data ingestion integrity: Yield = Production / Area.
3. Biological sanity bounds on authentic state statistics (Sugarcane, Onion, Tomato).
4. Experimental model notices & provenance breakdown in /api/crop/recommend.
5. New authentic crop endpoints (/api/crop/authentic-overview, /api/crop/authentic-records, /api/crop/provenance-registry).
6. Strict protection of canonical cotton dataset & production model hashes.
"""

import hashlib
from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import CANONICAL_COTTON_DATASET_PATH
from backend.ml.data_provenance_registry import (
    load_provenance_registry,
    get_datasets_by_classification,
    verify_dataset_integrity,
    is_synthetic_dataset
)

client = TestClient(app)

PROJECT_ROOT = Path("C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI")
AUTHENTIC_PANEL_PATH = PROJECT_ROOT / "data" / "authentic" / "processed" / "maharashtra_authentic_multi_crop_panel.csv"

PROTECTED_COTTON_DATASET_SHA256 = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PROTECTED_FINAL_MODEL_SHA256 = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

# ===========================================================================
# 1. PROVENANCE REGISTRY & CLASSIFICATION TESTS (WP3, WP4)
# ===========================================================================

def test_provenance_registry_structure_and_classifications():
    """Verify permanent provenance registry loads and contains all required classifications."""
    reg = load_provenance_registry()
    assert "registry_title" in reg
    assert "datasets" in reg
    
    valid_classes = set(reg["provenance_classifications"])
    assert "authentic_official_observation" in valid_classes
    assert "synthetic_benchmark" in valid_classes
    assert "authentic_research_observation" in valid_classes

    datasets = reg["datasets"]
    assert len(datasets) >= 6

    # Verify synthetic dataset is explicitly classified as synthetic_benchmark
    synth_entry = next((d for d in datasets if d["dataset_id"] == "maharashtra_agri_synthetic_benchmark"), None)
    assert synth_entry is not None
    assert synth_entry["classification"] == "synthetic_benchmark"
    assert synth_entry["is_synthetic"] is True

    # Verify cotton dataset is authentic_research_observation
    cotton_entry = next((d for d in datasets if d["dataset_id"] == "canonical_cotton_vidarbha_1997_2024"), None)
    assert cotton_entry is not None
    assert cotton_entry["classification"] == "authentic_research_observation"
    assert cotton_entry["is_synthetic"] is False

def test_is_synthetic_dataset_helper():
    """Verify helper identifies synthetic files accurately."""
    assert is_synthetic_dataset("data/raw/maharashtra_agri.csv") is True
    assert is_synthetic_dataset("data/vidarbha_cotton_model_ready_1997_2024.csv") is False
    assert is_synthetic_dataset("data/authentic/processed/maharashtra_authentic_multi_crop_panel.csv") is False

def test_verify_dataset_integrity_utility():
    """Verify SHA-256 checks against registered datasets."""
    res_cotton = verify_dataset_integrity("canonical_cotton_vidarbha_1997_2024")
    assert res_cotton["status"] == "verified_match"

    res_auth = verify_dataset_integrity("authentic_multi_crop_panel_maharashtra")
    assert res_auth["status"] == "verified_match"

# ===========================================================================
# 2. AUTHENTIC DATASET VERIFICATION & SANITY (WP2, WP6)
# ===========================================================================

def test_authentic_multi_crop_panel_yield_calculation():
    """Verify Yield = Production / Area on all authentic records (WP2)."""
    assert AUTHENTIC_PANEL_PATH.exists()
    df = pd.read_csv(AUTHENTIC_PANEL_PATH)
    assert len(df) >= 50

    for idx, row in df.iterrows():
        area = float(row["cultivated_area_ha"])
        prod = float(row["production_tonnes"])
        rep_yield_kg = float(row["reported_yield_kg_ha"])
        calc_yield_kg = float(row["calculated_yield_kg_ha"])
        
        # Area and production must be positive
        assert area > 0
        assert prod > 0

        # Independent calculation check
        expected_calc_kg = round((prod / area) * 1000.0, 1)
        assert abs(calc_yield_kg - expected_calc_kg) <= 0.2

        # Reported vs calculated yield match check
        discrepancy = float(row["yield_discrepancy_pct"])
        assert discrepancy < 1.0, f"Discrepancy too high for row {idx}: {discrepancy}%"
        assert row["verification_status"] == "verified_match"

def test_authentic_crop_biological_yield_ranges():
    """Verify authentic state crop yields fall within known biological limits for Maharashtra."""
    df = pd.read_csv(AUTHENTIC_PANEL_PATH)

    # Sugarcane: 50 - 150 t/ha in Maharashtra
    cane = df[df["crop"] == "Sugarcane"]
    assert len(cane) >= 20
    assert cane["calculated_yield_t_ha"].min() >= 60.0
    assert cane["calculated_yield_t_ha"].max() <= 120.0

    # Onion: 10 - 30 t/ha in Maharashtra
    onion = df[df["crop"] == "Onion"]
    assert len(onion) >= 15
    assert onion["calculated_yield_t_ha"].min() >= 12.0
    assert onion["calculated_yield_t_ha"].max() <= 25.0

    # Tomato: 12 - 40 t/ha in Maharashtra
    tomato = df[df["crop"] == "Tomato"]
    assert len(tomato) >= 12
    assert tomato["calculated_yield_t_ha"].min() >= 15.0
    assert tomato["calculated_yield_t_ha"].max() <= 35.0

# ===========================================================================
# 3. OPERATIONAL SAFETY & EXPERIMENTAL NOTICES (WP8)
# ===========================================================================

def test_crop_recommendation_returns_experimental_notice():
    """Verify /api/crop/recommend returns experimental notices and provenance badges."""
    payload = {
        "district": "Pune",
        "season": "Kharif",
        "temperature": 27.0,
        "rainfall": 200.0,
        "humidity": 65.0,
        "soil_nitrogen": 160.0,
        "soil_phosphorus": 24.0,
        "soil_potassium": 280.0,
        "soil_ph": 6.8,
        "soil_moisture": 60.0,
        "irrigation": True
    }
    res = client.post("/api/crop/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    # WP8: Explicit experimental notices
    assert data["is_experimental_model"] is True
    assert data["data_provenance"] == "synthetic_benchmark_plus_biophysical_rules"
    assert "experimental_model_notice" in data
    assert "synthetic benchmark" in data["experimental_model_notice"].lower()
    assert "provenance_breakdown" in data

    # Check each crop breakdown has biophysical and ML separation
    for rec in data["recommendations"]:
        assert "biophysical_suitability_score" in rec
        assert "ml_classifier_probability" in rec
        assert rec["ml_model_status"] == "experimental_synthetic"

# ===========================================================================
# 4. AUTHENTIC CROPS API ENDPOINTS (WP2, WP3)
# ===========================================================================

def test_authentic_crops_overview_endpoint():
    """Verify /api/crop/authentic-overview returns verified statistics."""
    res = client.get("/api/crop/authentic-overview")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["data_provenance"] == "authentic_official_observation"
    assert data["total_authentic_observations"] >= 50
    assert "Sugarcane" in data["crops"]
    assert "Onion" in data["crops"]
    assert "Tomato" in data["crops"]

def test_authentic_crops_records_endpoint_filtering():
    """Verify /api/crop/authentic-records supports crop and district filtering."""
    # Filter by Sugarcane
    res_cane = client.get("/api/crop/authentic-records?crop=Sugarcane")
    assert res_cane.status_code == 200
    cane_data = res_cane.json()
    assert all(r["crop"] == "Sugarcane" for r in cane_data["records"])

    # Filter by district Pune
    res_pune = client.get("/api/crop/authentic-records?district=Pune")
    assert res_pune.status_code == 200
    pune_data = res_pune.json()
    assert all(r["district"] == "Pune" for r in pune_data["records"])

def test_crop_provenance_registry_endpoint():
    """Verify /api/crop/provenance-registry returns full registry."""
    res = client.get("/api/crop/provenance-registry")
    assert res.status_code == 200
    data = res.json()
    assert "registry_title" in data
    assert "datasets" in data

# ===========================================================================
# 5. IMMUTABLE ASSET INTEGRITY (WP7, WP10)
# ===========================================================================

def test_protected_cotton_dataset_sha256_unmodified():
    """Verify data/vidarbha_cotton_model_ready_1997_2024.csv is bit-for-bit untouched."""
    content = CANONICAL_COTTON_DATASET_PATH.read_bytes()
    calculated = hashlib.sha256(content).hexdigest()
    assert calculated == PROTECTED_COTTON_DATASET_SHA256, (
        f"CRITICAL: Protected cotton dataset modified! Hash={calculated}"
    )

def test_protected_final_model_sha256_unmodified():
    """Verify backend/ml/artifacts/final_model.pkl is bit-for-bit untouched."""
    model_path = CANONICAL_COTTON_DATASET_PATH.parent.parent / "backend/ml/artifacts/final_model.pkl"
    content = model_path.read_bytes()
    calculated = hashlib.sha256(content).hexdigest()
    assert calculated == PROTECTED_FINAL_MODEL_SHA256, (
        f"CRITICAL: Protected final_model.pkl modified! Hash={calculated}"
    )
