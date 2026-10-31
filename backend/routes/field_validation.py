"""
FastAPI Routes for Field Validation, Soil Ingestion, and Outcome Tracking.

Provides:
- Soil test report ingestion & unit normalization (WP2)
- Field harvest observation logging & duplicate prevention (WP5, WP7)
- Prediction-versus-actual outcome tracking & error metrics (WP6)
- Taluka-level administrative verification (WP7)
- Weather provenance audit & Mahavedh status (WP3)
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.field_validation_schemas import (
    SoilTestReportRequest,
    FieldObservationRequest,
    OutcomeComparisonRequest,
    WithdrawConsentRequest,
    _generate_anonymous_farm_id
)
from backend.config import (
    DISTRICT_TALUKAS,
    MAHARASHTRA_DISTRICTS,
    PPM_TO_KG_PER_HA,
    PPM_TO_KG_PER_HA_METRIC,
    PPM_TO_KG_PER_HA_IMPERIAL,
    P2O5_TO_P,
    K2O_TO_K,
    QUINTAL_PER_ACRE_TO_KG_PER_HA,
    QUINTAL_PER_ACRE_TO_TONNES_PER_HA,
    TONNES_PER_HA_TO_KG_PER_HA
)
from backend.database.db import (
    save_soil_test_report,
    get_soil_test_reports,
    save_field_observation,
    get_field_observations,
    withdraw_field_observation_consent,
    record_outcome_comparison,
    get_outcome_comparisons,
    get_validation_summary
)
from backend.services.weather_provenance import (
    audit_weather_input_provenance,
    MAHAVEDH_INTEGRATION_STATUS,
    WEATHER_PROVENANCE_CATEGORIES
)

router = APIRouter(tags=["field_validation"])

# ===========================================================================
# 1. SOIL TEST REPORT INGESTION (WP2)
# ===========================================================================

@router.post("/api/soil/test-report", status_code=status.HTTP_201_CREATED)
def submit_soil_test_report(req: SoilTestReportRequest):
    """Safely ingest, validate, and standardize authentic laboratory soil test reports."""
    # Standardize units: convert ppm to kg/ha if needed
    factor = PPM_TO_KG_PER_HA if req.nitrogen_unit in ["ppm", "mg/kg"] else 1.0
    n_kg = req.nitrogen * factor
    p_factor = PPM_TO_KG_PER_HA if req.phosphorus_unit in ["ppm", "mg/kg"] else 1.0
    p_kg = req.phosphorus * p_factor
    k_factor = PPM_TO_KG_PER_HA if req.potassium_unit in ["ppm", "mg/kg"] else 1.0
    k_kg = req.potassium * k_factor

    # Handle oxide to elemental conversion if reported in oxide form (P2O5, K2O)
    p_elemental_kg = p_kg * (P2O5_TO_P if req.is_oxide_form else 1.0)
    k_elemental_kg = k_kg * (K2O_TO_K if req.is_oxide_form else 1.0)

    anon_id = _generate_anonymous_farm_id(req.farm_id)
    report_id = f"STR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    original_units = {
        "nitrogen": req.nitrogen_unit,
        "phosphorus": req.phosphorus_unit,
        "potassium": req.potassium_unit,
        "is_oxide_form": req.is_oxide_form,
        "extraction_method": req.extraction_method,
        "conversion_status": "estimated"
    }

    try:
        inserted_id = save_soil_test_report(
            report_id=report_id,
            anonymous_farm_id=anon_id,
            district=req.district,
            taluka=req.taluka,
            village=req.village,
            sampling_date=req.sampling_date,
            lab_name=req.lab_name,
            soil_ph=req.soil_ph,
            nitrogen_kg_ha=round(n_kg, 2),
            phosphorus_kg_ha=round(p_elemental_kg, 2),
            potassium_kg_ha=round(k_elemental_kg, 2),
            soil_moisture=req.soil_moisture,
            soil_type=req.soil_type,
            original_units=original_units,
            provenance_type=req.provenance_type,
            verification_status="verified" if req.provenance_type == "lab_measured" else "pending"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record soil report: {str(e)}")

    conversion_meta = {
        "conversion_status": "estimated",
        "bulk_density_assumed_g_cm3": req.bulk_density_g_cm3 or 1.33,
        "plough_layer_depth_cm": 15,
        "ppm_to_kg_ha_factor": PPM_TO_KG_PER_HA,
        "oxide_to_elemental_applied": req.is_oxide_form,
        "elemental_p_kg_ha": round(p_elemental_kg, 2),
        "elemental_k_kg_ha": round(k_elemental_kg, 2),
        "agronomic_disclaimer": (
            "Converted using standard 15cm plough layer bulk density assumptions (2.24 kg/ha per ppm). "
            "Actual laboratory extraction chemistry (Olsen vs Bray P, neutral 1N NH4OAc K) may introduce ±15% variance."
        )
    }

    return {
        "status": "success",
        "message": "Soil test report ingested and normalized successfully.",
        "report_id": report_id,
        "anonymous_farm_id": anon_id,
        "district": req.district,
        "taluka": req.taluka,
        "normalized_measurements": {
            "soil_ph": req.soil_ph,
            "nitrogen_kg_ha": round(n_kg, 2),
            "phosphorus_kg_ha": round(p_elemental_kg, 2),
            "potassium_kg_ha": round(k_elemental_kg, 2),
            "soil_moisture": req.soil_moisture
        },
        "provenance_type": req.provenance_type,
        "original_units": original_units,
        "conversion_metadata": conversion_meta
    }

@router.get("/api/soil/test-reports")
def list_soil_test_reports(
    district: Optional[str] = Query(None, description="Filter by Maharashtra district"),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve ingested soil test reports with masked farm identifiers."""
    reports = get_soil_test_reports(district=district, limit=limit)
    return {
        "status": "success",
        "count": len(reports),
        "district_filter": district,
        "reports": reports
    }

# ===========================================================================
# 2. FIELD HARVEST OBSERVATIONS (WP5, WP7)
# ===========================================================================

@router.post("/api/field-observations/record", status_code=status.HTTP_201_CREATED)
def submit_field_observation(req: FieldObservationRequest):
    """Record an authentic farmer harvest observation with biological validation & duplicate prevention."""
    anon_id = _generate_anonymous_farm_id(req.farm_id)
    obs_id = f"OBS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # Normalize yields to kg/ha and tonnes/ha
    u = req.yield_unit
    y = req.actual_yield
    if u == "quintal_per_acre":
        y_kg = y * QUINTAL_PER_ACRE_TO_KG_PER_HA
        y_t = y * QUINTAL_PER_ACRE_TO_TONNES_PER_HA
    elif u == "tonnes_per_ha":
        y_kg = y * TONNES_PER_HA_TO_KG_PER_HA
        y_t = y
    else:  # kg_per_ha
        y_kg = y
        y_t = y / TONNES_PER_HA_TO_KG_PER_HA

    # Duplicate check: check if same farm + crop + season + sowing date already recorded
    existing = get_field_observations(district=req.district, crop=req.crop, limit=200)
    for row in existing:
        if (
            row.get("anonymous_farm_id") == anon_id
            and row.get("season") == req.season
            and row.get("sowing_date") == req.sowing_date
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate observation detected: Farm {anon_id} already has a record for {req.crop} ({req.season} season, sowing {req.sowing_date})."
            )

    try:
        save_field_observation(
            observation_id=obs_id,
            anonymous_farm_id=anon_id,
            district=req.district,
            taluka=req.taluka,
            crop=req.crop,
            variety=req.variety,
            season=req.season,
            sowing_date=req.sowing_date,
            harvest_date=req.harvest_date,
            cultivated_area_ha=req.cultivated_area_ha,
            actual_yield=req.actual_yield,
            yield_unit=req.yield_unit,
            normalized_yield_kg_ha=round(y_kg, 2),
            normalized_yield_tonnes_ha=round(y_t, 2),
            irrigation_type=req.irrigation_type,
            total_rainfall_mm=req.total_rainfall_mm,
            stress_events=req.stress_events,
            data_source=req.data_source,
            consent_confirmed=req.consent_confirmed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record field observation: {str(e)}")

    return {
        "status": "success",
        "message": "Field harvest observation logged successfully.",
        "observation_id": obs_id,
        "anonymous_farm_id": anon_id,
        "crop": req.crop,
        "district": req.district,
        "taluka": req.taluka,
        "normalized_yield": {
            "kg_per_ha": round(y_kg, 2),
            "tonnes_per_ha": round(y_t, 2)
        },
        "data_source": req.data_source,
        "consent_confirmed": req.consent_confirmed
    }

@router.get("/api/field-observations")
def list_field_observations(
    district: Optional[str] = Query(None, description="Filter by Maharashtra district"),
    crop: Optional[str] = Query(None, description="Filter by crop (Cotton, Tomato, Onion, Sugarcane)"),
    include_withdrawn: bool = Query(False, description="Whether to include records where consent was withdrawn"),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve logged field harvest observations with consent filtering."""
    obs = get_field_observations(district=district, crop=crop, include_withdrawn=include_withdrawn, limit=limit)
    return {
        "status": "success",
        "count": len(obs),
        "observations": obs
    }

@router.post("/api/field-observations/withdraw-consent", status_code=status.HTTP_200_OK)
def withdraw_observation_consent(req: WithdrawConsentRequest):
    """
    Allow farmers or administrators to withdraw consent for field observations (WP6).
    The specified observation or all observations for this anonymous farm are marked
    consent_confirmed = 0, immediately excluding them from research queries.
    """
    count = withdraw_field_observation_consent(
        anonymous_farm_id=req.anonymous_farm_id,
        observation_id=req.observation_id
    )
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No matching active observations found for farm '{req.anonymous_farm_id}'"
        )
    return {
        "status": "success",
        "message": "Consent successfully withdrawn. Observation(s) excluded from active research queries.",
        "anonymous_farm_id": req.anonymous_farm_id,
        "observation_id": req.observation_id,
        "records_updated": count
    }

# ===========================================================================
# 3. OUTCOME COMPARISON & VALIDATION SUMMARY (WP4, WP6)
# ===========================================================================

@router.post("/api/outcomes/compare", status_code=status.HTTP_201_CREATED)
def record_prediction_outcome(req: OutcomeComparisonRequest):
    """Link a historical model prediction with an actual harvest outcome to track empirical error."""
    cmp_id = f"CMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    abs_err = abs(req.predicted_value - req.actual_value)
    pct_err = round((abs_err / max(0.001, req.actual_value)) * 100.0, 2)
    within_bounds = False
    if req.predicted_lower_bound is not None and req.predicted_upper_bound is not None:
        within_bounds = req.predicted_lower_bound <= req.actual_value <= req.predicted_upper_bound
    elif abs_err <= 0.15 * max(1.0, req.actual_value):
        within_bounds = True

    try:
        record_outcome_comparison(
            comparison_id=cmp_id,
            prediction_id=req.prediction_id,
            prediction_type=req.prediction_type,
            crop=req.crop,
            district=req.district,
            taluka=req.taluka,
            season=req.season,
            target_year=req.target_year,
            model_version=req.model_version,
            predicted_value=req.predicted_value,
            predicted_lower_bound=req.predicted_lower_bound,
            predicted_upper_bound=req.predicted_upper_bound,
            actual_value=req.actual_value,
            value_unit=req.value_unit,
            input_provenance=req.input_provenance,
            observation_source=req.observation_source,
            verification_status=req.verification_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record outcome comparison: {str(e)}")

    return {
        "status": "success",
        "message": "Prediction versus actual outcome comparison recorded.",
        "comparison_id": cmp_id,
        "crop": req.crop,
        "district": req.district,
        "predicted_value": req.predicted_value,
        "actual_value": req.actual_value,
        "absolute_error": round(abs_err, 2),
        "percentage_error": pct_err,
        "is_within_error_bound": within_bounds,
        "model_version": req.model_version
    }

@router.get("/api/outcomes/summary")
def get_outcome_validation_summary():
    """Retrieve validation summary with sample-size thresholds and empirical error metrics."""
    return get_validation_summary()

# ===========================================================================
# 4. ADMINISTRATIVE & WEATHER PROVENANCE (WP3, WP7)
# ===========================================================================

@router.get("/api/talukas/{district}")
def get_district_talukas(district: str):
    """Retrieve verified talukas for an administrative district in Maharashtra."""
    norm = None
    for d in MAHARASHTRA_DISTRICTS:
        if d.lower() == district.strip().lower():
            norm = d
            break
    if not norm:
        raise HTTPException(status_code=404, detail=f"District '{district}' not found in Maharashtra.")
    talukas = DISTRICT_TALUKAS.get(norm, [])
    return {
        "status": "success",
        "district": norm,
        "total_talukas": len(talukas),
        "talukas": talukas
    }

@router.get("/api/weather-provenance/{district}")
def get_district_weather_provenance(district: str):
    """Inspect and audit meteorological data provenance and Mahavedh integration status."""
    norm = None
    for d in MAHARASHTRA_DISTRICTS:
        if d.lower() == district.strip().lower():
            norm = d
            break
    if not norm:
        norm = "Pune"

    audit = audit_weather_input_provenance({"district": norm, "is_live_api": True, "provider": "Open-Meteo"})
    return {
        "status": "success",
        "audit": audit,
        "mahavedh_status": MAHAVEDH_INTEGRATION_STATUS,
        "provenance_categories": WEATHER_PROVENANCE_CATEGORIES
    }
