"""
Phase 11 Automated Test Suite: Real Agricultural Data Integration & Field Validation Infrastructure.

Covers:
- Soil test report ingestion & unit normalization (ppm -> kg/ha)
- Taluka-district administrative mismatch validation
- Chronological ordering & future date leakage prevention
- Biological yield boundary checks
- Duplicate observation detection (409 Conflict)
- Privacy masking and anonymized farm identifiers
- Outcome tracking & error calculation
- Minimum sample size threshold & statistical disclaimers
- Weather data provenance & Mahavedh network status
- Strict canonical dataset and production model hash protection
"""

import pytest
import uuid
from datetime import date, timedelta
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import (
    CANONICAL_COTTON_DATASET_PATH,
    DISTRICT_TALUKAS,
    PPM_TO_KG_PER_HA,
    QUINTAL_PER_ACRE_TO_KG_PER_HA
)
import hashlib

client = TestClient(app)

PROTECTED_COTTON_DATASET_SHA256 = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PROTECTED_FINAL_MODEL_SHA256 = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

# ===========================================================================
# 1. SOIL TEST REPORT INGESTION TESTS (WP2, WP7)
# ===========================================================================

def test_soil_test_report_ingestion_ppm_conversion():
    payload = {
        "district": "Akola",
        "taluka": "Akot",
        "village": "Chondi",
        "sampling_date": "2026-05-10",
        "lab_name": "Dr. PDKV Soil Testing Lab",
        "soil_ph": 7.5,
        "nitrogen": 80.0,
        "nitrogen_unit": "ppm",
        "phosphorus": 10.0,
        "phosphorus_unit": "ppm",
        "potassium": 140.0,
        "potassium_unit": "ppm",
        "soil_moisture": 58.0,
        "soil_type": "Deep Black Vertisol",
        "provenance_type": "lab_measured"
    }
    res = client.post("/api/soil/test-report", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["report_id"].startswith("STR-")
    assert data["anonymous_farm_id"].startswith("FARM-")
    assert data["district"] == "Akola"
    assert data["taluka"] == "Akot"

    # Verify unit conversion (80 ppm * 2.24 = 179.2 kg/ha)
    expected_n = round(80.0 * PPM_TO_KG_PER_HA, 2)
    assert abs(data["normalized_measurements"]["nitrogen_kg_ha"] - expected_n) < 0.1

def test_soil_test_report_invalid_unit_rejected():
    payload = {
        "district": "Akola",
        "taluka": "Akot",
        "sampling_date": "2026-05-10",
        "soil_ph": 7.5,
        "nitrogen": 80.0,
        "nitrogen_unit": "lbs_per_acre",  # Invalid unit
        "phosphorus": 10.0,
        "phosphorus_unit": "kg/ha",
        "potassium": 140.0,
        "potassium_unit": "kg/ha"
    }
    res = client.post("/api/soil/test-report", json=payload)
    assert res.status_code == 422

def test_soil_test_report_district_taluka_mismatch():
    payload = {
        "district": "Akola",
        "taluka": "Baramati",  # Baramati belongs to Pune, not Akola!
        "sampling_date": "2026-05-10",
        "soil_ph": 7.5,
        "nitrogen": 160.0,
        "phosphorus": 22.0,
        "potassium": 280.0
    }
    res = client.post("/api/soil/test-report", json=payload)
    assert res.status_code == 422

def test_soil_test_report_future_date_rejected():
    tomorrow = (date.today() + timedelta(days=2)).isoformat()
    payload = {
        "district": "Akola",
        "taluka": "Akot",
        "sampling_date": tomorrow,  # Future date!
        "soil_ph": 7.5,
        "nitrogen": 160.0,
        "phosphorus": 22.0,
        "potassium": 280.0
    }
    res = client.post("/api/soil/test-report", json=payload)
    assert res.status_code == 422

# ===========================================================================
# 2. FIELD HARVEST OBSERVATION TESTS (WP5, WP7, WP8)
# ===========================================================================

def test_field_observation_ingestion_and_normalization():
    fid = f"FARM-TEST-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "farm_id": fid,
        "district": "Amravati",
        "taluka": "Achalpur",
        "crop": "Cotton",
        "variety": "Ajeet-155",
        "season": "Kharif",
        "sowing_date": "2025-06-20",
        "harvest_date": "2025-11-25",
        "cultivated_area_ha": 2.0,
        "actual_yield": 4.5,
        "yield_unit": "quintal_per_acre",
        "irrigation_type": "protective_drip",
        "total_rainfall_mm": 820.0,
        "data_source": "extension_verified",
        "consent_confirmed": True
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["observation_id"].startswith("OBS-")
    assert data["anonymous_farm_id"] == fid
    
    # 4.5 quintal/acre * 247.105 = 1111.97 kg/ha
    expected_kg = round(4.5 * QUINTAL_PER_ACRE_TO_KG_PER_HA, 2)
    assert abs(data["normalized_yield"]["kg_per_ha"] - expected_kg) < 1.0

def test_field_observation_sowing_after_harvest_rejected():
    payload = {
        "district": "Amravati",
        "taluka": "Achalpur",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-11-25",  # Sowing AFTER harvest!
        "harvest_date": "2025-06-20",
        "cultivated_area_ha": 2.0,
        "actual_yield": 800.0,
        "yield_unit": "kg_per_ha"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 422

def test_field_observation_unrealistic_growth_period_rejected():
    payload = {
        "district": "Amravati",
        "taluka": "Achalpur",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-06-20",
        "harvest_date": "2025-07-05",  # Only 15 days growth period!
        "cultivated_area_ha": 2.0,
        "actual_yield": 800.0,
        "yield_unit": "kg_per_ha"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 422

def test_field_observation_biological_yield_limits():
    payload = {
        "district": "Amravati",
        "taluka": "Achalpur",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-06-20",
        "harvest_date": "2025-11-20",
        "cultivated_area_ha": 2.0,
        "actual_yield": 8500.0,  # 8,500 kg/ha is biologically impossible for rainfed Indian cotton!
        "yield_unit": "kg_per_ha"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 422

def test_field_observation_duplicate_prevention():
    fid = f"FARM-DUP-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "farm_id": fid,
        "district": "Wardha",
        "taluka": "Seloo",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-06-15",
        "harvest_date": "2025-11-15",
        "cultivated_area_ha": 1.5,
        "actual_yield": 920.0,
        "yield_unit": "kg_per_ha"
    }
    # First submission -> 201 Created
    res1 = client.post("/api/field-observations/record", json=payload)
    assert res1.status_code == 201

    # Second identical submission -> 409 Conflict
    res2 = client.post("/api/field-observations/record", json=payload)
    assert res2.status_code == 409
    assert "Duplicate observation detected" in res2.json()["detail"]

# ===========================================================================
# 3. OUTCOME COMPARISON & VALIDATION SUMMARY (WP4, WP6, WP9)
# ===========================================================================

def test_outcome_comparison_recording_and_error_calculation():
    payload = {
        "prediction_id": 101,
        "prediction_type": "cotton_yield",
        "crop": "Cotton",
        "district": "Akola",
        "taluka": "Akot",
        "season": "Kharif",
        "target_year": 2024,
        "model_version": "candidate_six_district_thermal",
        "predicted_value": 1050.0,
        "predicted_lower_bound": 796.5,
        "predicted_upper_bound": 1303.5,
        "actual_value": 980.0,
        "value_unit": "kg/ha",
        "input_provenance": "shc_benchmark",
        "observation_source": "farmer_reported"
    }
    res = client.post("/api/outcomes/compare", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["absolute_error"] == 70.0
    assert abs(data["percentage_error"] - 7.14) < 0.1
    assert data["is_within_error_bound"] is True

def test_outcome_summary_sample_size_threshold():
    res = client.get("/api/outcomes/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "crops" in data
    # When sample size N < 10, aggregate accuracy metrics must be withheld
    for crop in ["Tomato", "Onion", "Sugarcane"]:
        crop_data = data["crops"][crop]
        if crop_data["sample_size_n"] < 10:
            assert crop_data["statistical_reliability"] == "insufficient_data"
            assert crop_data["mean_absolute_error"] is None
            assert "below statistical minimum" in crop_data["disclaimer"]

# ===========================================================================
# 4. WEATHER PROVENANCE & TALUKA REGISTRY TESTS (WP3, WP7)
# ===========================================================================

def test_weather_provenance_and_mahavedh_status():
    res = client.get("/api/weather-provenance/Akola")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["mahavedh_status"]["integration_state"] == "credentials_required"
    assert data["mahavedh_status"]["public_api_available"] is False
    assert "historical_observation" in data["provenance_categories"]
    assert "live_telemetry" in data["provenance_categories"]

def test_talukas_endpoint_valid_district():
    res = client.get("/api/talukas/Akola")
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "Akola"
    assert "Akot" in data["talukas"]
    assert "Balapur" in data["talukas"]

def test_talukas_endpoint_unknown_district():
    res = client.get("/api/talukas/NonExistentDistrict")
    assert res.status_code == 404

# ===========================================================================
# 5. STRICT ASSET HASH PROTECTION VERIFICATION
# ===========================================================================

def test_canonical_cotton_dataset_hash_unmodified():
    with open(CANONICAL_COTTON_DATASET_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash.lower() == PROTECTED_COTTON_DATASET_SHA256.lower()

def test_final_model_artifact_hash_unmodified():
    model_path = CANONICAL_COTTON_DATASET_PATH.parent.parent / "backend" / "ml" / "artifacts" / "final_model.pkl"
    with open(model_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash.lower() == PROTECTED_FINAL_MODEL_SHA256.lower()
