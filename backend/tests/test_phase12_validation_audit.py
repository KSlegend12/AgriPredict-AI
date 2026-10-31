"""
Phase 12 Automated Test Suite: Independent Validation Audit, Leakage Investigation & Evidence Integrity.

Covers:
1. Crop-specific biological duration validation (Cotton, Tomato, Onion, Sugarcane).
2. Salted HMAC anonymous farm ID hashing and quasi-identifier village masking.
3. Farmer consent withdrawal endpoint (POST /api/field-observations/withdraw-consent).
4. Soil unit conversion audit (oxide vs elemental stoichiometry and disclaimer).
5. Immutable protected asset hash preservation.
"""

import uuid
import hashlib
import hmac
from datetime import date, timedelta
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import (
    CANONICAL_COTTON_DATASET_PATH,
    FARM_ID_HMAC_SALT,
    P2O5_TO_P,
    K2O_TO_K,
    PPM_TO_KG_PER_HA,
    CROP_GROWTH_DURATION_DAYS
)
from backend.schemas.field_validation_schemas import _generate_anonymous_farm_id

client = TestClient(app)

PROTECTED_COTTON_DATASET_SHA256 = "1430370e066b41431cc164fb6f12759f7d1e97bb1cb4f590f77cad2b4ee53091"
PROTECTED_FINAL_MODEL_SHA256 = "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e"

# ===========================================================================
# 1. CROP-SPECIFIC BIOLOGICAL DURATION TESTS (WP7)
# ===========================================================================

def test_non_cotton_field_observation_rejected():
    """Non-cotton crops like Sugarcane must be rejected (only Cotton allowed)."""
    payload = {
        "district": "Pune",
        "taluka": "Baramati",
        "crop": "Sugarcane",
        "season": "Kharif",
        "sowing_date": "2025-01-15",
        "harvest_date": "2025-06-15",
        "cultivated_area_ha": 3.0,
        "actual_yield": 85.0,
        "yield_unit": "tonnes_per_ha"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 422

def test_cotton_valid_duration_accepted():
    """Cotton harvested in 160 days must pass validation."""
    fid = f"FARM-TEST-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "farm_id": fid,
        "district": "Akola",
        "taluka": "Akot",
        "crop": "Cotton",
        "variety": "Bt-Cotton",
        "season": "Kharif",
        "sowing_date": "2024-06-15",
        "harvest_date": "2024-11-22",  # 160 days
        "cultivated_area_ha": 2.0,
        "actual_yield": 850.0,
        "yield_unit": "kg_per_ha",
        "irrigation_type": "rainfed"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["crop"] == "Cotton"

def test_cotton_short_duration_rejected():
    """Cotton harvested in 60 days must be rejected (min 120 days)."""
    payload = {
        "district": "Akola",
        "taluka": "Akot",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-06-15",
        "harvest_date": "2025-08-30",  # 76 days
        "cultivated_area_ha": 2.0,
        "actual_yield": 800.0,
        "yield_unit": "kg_per_ha"
    }
    res = client.post("/api/field-observations/record", json=payload)
    assert res.status_code == 422
    assert "minimum duration is 120" in res.text

def test_tomato_field_observation_rejected():
    """Tomato observations must be rejected under Cotton-only scope."""
    p_short = {
        "district": "Nashik",
        "taluka": "Niphad",
        "crop": "Tomato",
        "season": "Rabi",
        "sowing_date": "2025-10-01",
        "harvest_date": "2025-11-10",
        "cultivated_area_ha": 1.0,
        "actual_yield": 30.0,
        "yield_unit": "tonnes_per_ha"
    }
    res_short = client.post("/api/field-observations/record", json=p_short)
    assert res_short.status_code == 422

# ===========================================================================
# 2. PRIVACY & SALTED HMAC FARM ID HASHING (WP6)
# ===========================================================================

def test_salted_hmac_anonymization():
    """Ensure farm ID anonymization uses HMAC with server-side salt."""
    raw_phone = "9822099999"
    anon1 = _generate_anonymous_farm_id(raw_phone)
    anon2 = _generate_anonymous_farm_id(raw_phone)
    
    assert anon1 == anon2, "HMAC hashing must be deterministic for identical input and salt"
    assert anon1.startswith("FARM-")
    assert raw_phone not in anon1
    
    # Verify manual HMAC matches
    expected_hex = hmac.new(
        FARM_ID_HMAC_SALT.encode("utf-8"),
        raw_phone.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:12].upper()
    assert anon1 == f"FARM-{expected_hex}"

def test_village_masking_in_soil_reports():
    """Quasi-identifier protection: village name must be masked in report listings."""
    # Submit report with village
    payload = {
        "district": "Wardha",
        "taluka": "Hinganghat",
        "village": "Wadner",
        "sampling_date": "2026-04-10",
        "soil_ph": 7.2,
        "nitrogen": 170.0,
        "phosphorus": 24.0,
        "potassium": 290.0
    }
    sub_res = client.post("/api/soil/test-report", json=payload)
    assert sub_res.status_code == 201

    # Query listings
    list_res = client.get("/api/soil/test-reports?district=Wardha")
    assert list_res.status_code == 200
    reports = list_res.json()["reports"]
    assert len(reports) > 0
    # Village must be masked
    for r in reports:
        if r.get("village"):
            assert r["village"] == "[MASKED]"

# ===========================================================================
# 3. CONSENT WITHDRAWAL TESTS (WP6)
# ===========================================================================

def test_field_observation_consent_withdrawal():
    """Farmer can withdraw consent; observation is immediately excluded from queries."""
    fid = f"FARM-TEST-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "farm_id": fid,
        "district": "Nagpur",
        "taluka": "Katol",
        "crop": "Cotton",
        "season": "Kharif",
        "sowing_date": "2025-06-15",
        "harvest_date": "2025-11-20",  # 158 days
        "cultivated_area_ha": 2.5,
        "actual_yield": 950.0,
        "yield_unit": "kg_per_ha",
        "consent_confirmed": True
    }
    rec_res = client.post("/api/field-observations/record", json=payload)
    assert rec_res.status_code == 201
    obs_id = rec_res.json()["observation_id"]

    # Verify present in listing
    pre_res = client.get(f"/api/field-observations?district=Nagpur&crop=Cotton")
    assert pre_res.status_code == 200
    found_pre = any(o["observation_id"] == obs_id for o in pre_res.json()["observations"])
    assert found_pre is True

    # Withdraw consent
    w_res = client.post("/api/field-observations/withdraw-consent", json={
        "anonymous_farm_id": fid,
        "observation_id": obs_id,
        "reason": "Farmer withdrew research consent"
    })
    assert w_res.status_code == 200
    assert w_res.json()["records_updated"] >= 1

    # Verify excluded in default listing
    post_res = client.get(f"/api/field-observations?district=Nagpur&crop=Cotton")
    assert post_res.status_code == 200
    found_post = any(o["observation_id"] == obs_id for o in post_res.json()["observations"])
    assert found_post is False

    # Verify present when include_withdrawn=True is explicitly queried
    withdrawn_res = client.get(f"/api/field-observations?district=Nagpur&crop=Cotton&include_withdrawn=true")
    assert withdrawn_res.status_code == 200
    w_obs = next((o for o in withdrawn_res.json()["observations"] if o["observation_id"] == obs_id), None)
    assert w_obs is not None
    assert w_obs["consent_confirmed"] == 0

def test_withdraw_consent_nonexistent_farm_returns_404():
    """Attempting to withdraw consent for an unregistered farm returns 404."""
    w_res = client.post("/api/field-observations/withdraw-consent", json={
        "anonymous_farm_id": "FARM-NONEXISTENT-9999"
    })
    assert w_res.status_code == 404

# ===========================================================================
# 4. SOIL CONVERSION & OXIDE TRACKING (WP4)
# ===========================================================================

def test_soil_oxide_form_conversion():
    """Verify conversion of P2O5 and K2O to elemental P and K."""
    payload = {
        "district": "Washim",
        "taluka": "Risod",
        "sampling_date": "2026-05-01",
        "soil_ph": 7.4,
        "nitrogen": 160.0,
        "nitrogen_unit": "kg/ha",
        "phosphorus": 45.0,  # 45 kg/ha P2O5
        "phosphorus_unit": "kg/ha",
        "potassium": 300.0,  # 300 kg/ha K2O
        "potassium_unit": "kg/ha",
        "is_oxide_form": True
    }
    res = client.post("/api/soil/test-report", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["conversion_metadata"]["conversion_status"] == "estimated"
    assert data["conversion_metadata"]["oxide_to_elemental_applied"] is True

    # P2O5 * 0.4364 = 45 * 0.4364 = 19.64 kg/ha elemental P
    expected_p = round(45.0 * P2O5_TO_P, 2)
    assert abs(data["normalized_measurements"]["phosphorus_kg_ha"] - expected_p) < 0.1

    # K2O * 0.8302 = 300 * 0.8302 = 249.06 kg/ha elemental K
    expected_k = round(300.0 * K2O_TO_K, 2)
    assert abs(data["normalized_measurements"]["potassium_kg_ha"] - expected_k) < 0.1

# ===========================================================================
# 5. IMMUTABLE ASSET INTEGRITY (WP10)
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
