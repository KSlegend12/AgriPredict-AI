"""
Pydantic V2 Schemas for Authentic Agricultural Data Ingestion & Field Validation.

Enforces:
- District & Taluka administrative matching
- Strict unit normalization (ppm to kg/ha)
- Plausible biological yield constraints
- Chronological ordering (sowing_date <= harvest_date <= today)
- Privacy masking (anonymous farm identifiers)
- Provenance tagging (lab_measured vs shc_benchmark vs user_estimate)
"""

import hashlib
import hmac
import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.config import (
    MAHARASHTRA_DISTRICTS,
    DISTRICT_TALUKAS,
    ALLOWED_CROPS,
    PPM_TO_KG_PER_HA,
    PPM_TO_KG_PER_HA_METRIC,
    PPM_TO_KG_PER_HA_IMPERIAL,
    P2O5_TO_P,
    K2O_TO_K,
    CROP_GROWTH_DURATION_DAYS,
    FARM_ID_HMAC_SALT,
    QUINTAL_PER_ACRE_TO_KG_PER_HA,
    QUINTAL_PER_ACRE_TO_TONNES_PER_HA,
    TONNES_PER_HA_TO_KG_PER_HA
)

def _normalize_name(v: str) -> str:
    cleaned = v.strip()
    for d in MAHARASHTRA_DISTRICTS:
        if d.lower() == cleaned.lower():
            return d
    return cleaned

def _generate_anonymous_farm_id(raw_id: Optional[str] = None) -> str:
    """
    Generate or cryptographically hash an anonymous farm identifier without storing PII.
    Uses HMAC-SHA256 with a server-side secret salt to protect against dictionary/rainbow-table attacks
    on phone numbers or 7/12 land survey numbers.
    """
    if not raw_id:
        return f"FARM-{uuid.uuid4().hex[:10].upper()}"
    # If already formatted as FARM-XXXX, keep it
    if raw_id.startswith("FARM-") and len(raw_id) >= 10:
        return raw_id
    # Keyed HMAC-SHA256 hash to protect privacy against rainbow tables
    hashed = hmac.new(
        FARM_ID_HMAC_SALT.encode("utf-8"),
        raw_id.strip().encode("utf-8"),
        hashlib.sha256
    ).hexdigest()[:12].upper()
    return f"FARM-{hashed}"

# ===========================================================================
# 1. SOIL TEST REPORT SCHEMAS
# ===========================================================================

class SoilTestReportRequest(BaseModel):
    district: str = Field(..., json_schema_extra={"example": "Akola"})
    taluka: str = Field(..., json_schema_extra={"example": "Akot"})
    village: Optional[str] = Field(None, json_schema_extra={"example": "Chondi"})
    farm_id: Optional[str] = Field(None, json_schema_extra={"example": "FARM-A9F32104"})
    sampling_date: str = Field(..., json_schema_extra={"example": "2026-05-15"})
    lab_name: Optional[str] = Field(None, json_schema_extra={"example": "Dr. PDKV Soil Testing Laboratory"})
    soil_ph: float = Field(..., ge=3.0, le=11.0, json_schema_extra={"example": 7.6})
    nitrogen: float = Field(..., ge=0.0, le=600.0, json_schema_extra={"example": 165.0})
    nitrogen_unit: str = Field("kg/ha", json_schema_extra={"example": "kg/ha"})
    phosphorus: float = Field(..., ge=0.0, le=400.0, json_schema_extra={"example": 22.0})
    phosphorus_unit: str = Field("kg/ha", json_schema_extra={"example": "kg/ha"})
    potassium: float = Field(..., ge=0.0, le=600.0, json_schema_extra={"example": 320.0})
    potassium_unit: str = Field("kg/ha", json_schema_extra={"example": "kg/ha"})
    soil_moisture: Optional[float] = Field(None, ge=0.0, le=100.0, json_schema_extra={"example": 58.0})
    soil_type: Optional[str] = Field(None, json_schema_extra={"example": "Deep Black Vertisol"})
    provenance_type: str = Field("lab_measured", json_schema_extra={"example": "lab_measured"})
    is_oxide_form: bool = Field(False, json_schema_extra={"example": False})
    bulk_density_g_cm3: Optional[float] = Field(1.33, ge=0.5, le=2.5, json_schema_extra={"example": 1.33})
    extraction_method: Optional[str] = Field("Olsen/AmmoniumAcetate", json_schema_extra={"example": "Olsen/AmmoniumAcetate"})
    conversion_status: Optional[str] = Field("estimated", json_schema_extra={"example": "estimated"})

    @field_validator("district")
    def validate_district(cls, v):
        norm = _normalize_name(v)
        if norm not in MAHARASHTRA_DISTRICTS:
            raise ValueError(f"Unknown district '{v}'. Must be a valid Maharashtra district.")
        return norm

    @field_validator("provenance_type")
    def validate_provenance(cls, v):
        valid = {"lab_measured", "shc_benchmark", "user_estimate"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid provenance_type '{v}'. Must be one of: {', '.join(valid)}")
        return v.lower()

    @field_validator("nitrogen_unit", "phosphorus_unit", "potassium_unit")
    def validate_units(cls, v):
        valid = {"kg/ha", "kg_per_ha", "ppm", "mg/kg"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid unit '{v}'. Must be one of: {', '.join(valid)}")
        return v.lower()

    @field_validator("sampling_date")
    def validate_date(cls, v):
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
            if d > date.today():
                raise ValueError(f"Sampling date '{v}' cannot be in the future.")
        except ValueError as e:
            if "Sampling date" in str(e):
                raise
            raise ValueError(f"Invalid date format '{v}'. Expected YYYY-MM-DD.")
        return v

    @model_validator(mode="after")
    def validate_district_taluka(self):
        talukas = DISTRICT_TALUKAS.get(self.district, [])
        if talukas and self.taluka.strip().title() not in [t.title() for t in talukas]:
            raise ValueError(
                f"Taluka '{self.taluka}' does not belong to district '{self.district}'. "
                f"Valid talukas: {', '.join(talukas[:8])}..."
            )
        return self

# ===========================================================================
# 2. FIELD HARVEST OBSERVATION SCHEMAS
# ===========================================================================

class FieldObservationRequest(BaseModel):
    farm_id: Optional[str] = Field(None, json_schema_extra={"example": "FARM-B82103"})
    district: str = Field(..., json_schema_extra={"example": "Akola"})
    taluka: str = Field(..., json_schema_extra={"example": "Akot"})
    crop: str = Field(..., json_schema_extra={"example": "Cotton"})
    variety: Optional[str] = Field(None, json_schema_extra={"example": "Bt-Cotton RCH-2"})
    season: str = Field(..., json_schema_extra={"example": "Kharif"})
    sowing_date: str = Field(..., json_schema_extra={"example": "2025-06-25"})
    harvest_date: str = Field(..., json_schema_extra={"example": "2025-11-20"})
    cultivated_area_ha: float = Field(..., ge=0.05, le=500.0, json_schema_extra={"example": 2.0})
    actual_yield: float = Field(..., ge=0.1, le=10000.0, json_schema_extra={"example": 1420.0})
    yield_unit: str = Field("kg_per_ha", json_schema_extra={"example": "kg_per_ha"})
    irrigation_type: Optional[str] = Field("rainfed", json_schema_extra={"example": "rainfed"})
    total_rainfall_mm: Optional[float] = Field(None, ge=0.0, le=5000.0, json_schema_extra={"example": 780.0})
    stress_events: Optional[List[str]] = Field(default_factory=list, json_schema_extra={"example": ["dry_spell_14_days"]})
    data_source: str = Field("farmer_reported", json_schema_extra={"example": "farmer_reported"})
    consent_confirmed: bool = Field(True, json_schema_extra={"example": True})

    @field_validator("district")
    def validate_district(cls, v):
        norm = _normalize_name(v)
        if norm not in MAHARASHTRA_DISTRICTS:
            raise ValueError(f"Unknown district '{v}'. Must be a valid Maharashtra district.")
        return norm

    @field_validator("crop")
    def validate_crop(cls, v):
        cleaned = v.strip().capitalize()
        if cleaned not in ALLOWED_CROPS:
            raise ValueError(f"Crop '{v}' not supported. AgriPredict-AI is strictly dedicated to Cotton (allowed: {', '.join(ALLOWED_CROPS)}).")
        return cleaned

    @field_validator("season")
    def validate_season(cls, v):
        valid = {"Kharif", "Rabi", "Summer"}
        if v.strip().capitalize() not in valid:
            raise ValueError(f"Season '{v}' invalid. Must be Kharif, Rabi, or Summer.")
        return v.strip().capitalize()

    @field_validator("yield_unit")
    def validate_unit(cls, v):
        valid = {"kg_per_ha", "tonnes_per_ha", "quintal_per_acre"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid yield_unit '{v}'. Must be one of: {', '.join(valid)}")
        return v.lower()

    @field_validator("data_source")
    def validate_source(cls, v):
        valid = {"farmer_reported", "extension_verified", "university_trial"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid data_source '{v}'. Must be one of: {', '.join(valid)}")
        return v.lower()

    @model_validator(mode="after")
    def validate_temporal_and_biological_constraints(self):
        # 1. District - Taluka match
        talukas = DISTRICT_TALUKAS.get(self.district, [])
        if talukas and self.taluka.strip().title() not in [t.title() for t in talukas]:
            raise ValueError(f"Taluka '{self.taluka}' does not belong to district '{self.district}'.")

        # 2. Sowing before Harvest & Crop-Specific Biological Duration (WP7)
        try:
            s_date = datetime.strptime(self.sowing_date, "%Y-%m-%d").date()
            h_date = datetime.strptime(self.harvest_date, "%Y-%m-%d").date()
            if s_date > h_date:
                raise ValueError(f"Sowing date ({self.sowing_date}) cannot be after harvest date ({self.harvest_date}).")
            if h_date > date.today():
                raise ValueError(f"Harvest date ({self.harvest_date}) cannot be in the future.")
            duration_days = (h_date - s_date).days
            
            limits = CROP_GROWTH_DURATION_DAYS.get(self.crop)
            if limits:
                min_d = limits["min_days"]
                max_d = limits["max_days"]
                if duration_days < min_d:
                    raise ValueError(
                        f"Growth duration for {self.crop} ({duration_days} days) is biologically implausible: "
                        f"minimum duration is {min_d} days (typical: {limits['typical_days']} days)."
                    )
                if duration_days > max_d:
                    raise ValueError(
                        f"Growth duration for {self.crop} ({duration_days} days) exceeds biological limit: "
                        f"maximum plausible duration is {max_d} days."
                    )
            elif duration_days < 45:
                raise ValueError(f"Crop growth period ({duration_days} days) is unrealistically short (<45 days).")
        except ValueError as e:
            if "Sowing date" in str(e) or "Harvest date" in str(e) or "Growth duration" in str(e) or "growth period" in str(e):
                raise
            raise ValueError("Invalid date format. Expected YYYY-MM-DD.")

        # 3. Biological yield sanity bounds per crop
        c = self.crop
        y = self.actual_yield
        u = self.yield_unit

        # Normalize to kg/ha for check
        if u == "quintal_per_acre":
            y_kg = y * QUINTAL_PER_ACRE_TO_KG_PER_HA
        elif u == "tonnes_per_ha":
            y_kg = y * TONNES_PER_HA_TO_KG_PER_HA
        else:
            y_kg = y

        if c == "Cotton" and (y_kg < 50.0 or y_kg > 3500.0):
            raise ValueError(f"Cotton yield {y_kg:.1f} kg/ha is outside biological limits (50 - 3500 kg/ha).")
        elif c in ["Tomato", "Onion"] and (y_kg < 1000.0 or y_kg > 150000.0):
            raise ValueError(f"{c} yield {y_kg/1000.0:.1f} t/ha is outside biological limits (1 - 150 t/ha).")
        elif c == "Sugarcane" and (y_kg < 10000.0 or y_kg > 300000.0):
            raise ValueError(f"Sugarcane yield {y_kg/1000.0:.1f} t/ha is outside biological limits (10 - 300 t/ha).")

        return self

# ===========================================================================
# 3. OUTCOME COMPARISON SCHEMAS
# ===========================================================================

class OutcomeComparisonRequest(BaseModel):
    prediction_id: Optional[int] = Field(None, json_schema_extra={"example": 105})
    prediction_type: str = Field("cotton_yield", json_schema_extra={"example": "cotton_yield"})
    crop: str = Field(..., json_schema_extra={"example": "Cotton"})
    district: str = Field(..., json_schema_extra={"example": "Akola"})
    taluka: Optional[str] = Field(None, json_schema_extra={"example": "Akot"})
    season: str = Field("Kharif", json_schema_extra={"example": "Kharif"})
    target_year: int = Field(2024, ge=1997, le=2030, json_schema_extra={"example": 2024})
    model_version: str = Field("candidate_six_district_thermal", json_schema_extra={"example": "candidate_six_district_thermal"})
    predicted_value: float = Field(..., ge=0.0, json_schema_extra={"example": 1025.4})
    predicted_lower_bound: Optional[float] = Field(None, json_schema_extra={"example": 771.9})
    predicted_upper_bound: Optional[float] = Field(None, json_schema_extra={"example": 1278.9})
    actual_value: float = Field(..., ge=0.0, json_schema_extra={"example": 980.0})
    value_unit: str = Field("kg/ha", json_schema_extra={"example": "kg/ha"})
    input_provenance: str = Field("shc_benchmark", json_schema_extra={"example": "shc_benchmark"})
    observation_source: str = Field("farmer_reported", json_schema_extra={"example": "farmer_reported"})
    verification_status: str = Field("unverified", json_schema_extra={"example": "unverified"})

    @field_validator("crop")
    def validate_crop(cls, v):
        cleaned = v.strip().capitalize()
        if cleaned not in ALLOWED_CROPS:
            raise ValueError(f"Crop '{v}' not supported. AgriPredict-AI is strictly dedicated to Cotton.")
        return cleaned

# ===========================================================================
# 4. PRIVACY & CONSENT WITHDRAWAL SCHEMAS (WP6)
# ===========================================================================

class WithdrawConsentRequest(BaseModel):
    anonymous_farm_id: str = Field(..., json_schema_extra={"example": "FARM-A9F32104B8"})
    observation_id: Optional[str] = Field(None, json_schema_extra={"example": "OBS-20261031-1A2B3C"})
    reason: Optional[str] = Field(None, json_schema_extra={"example": "Farmer requested record removal"})

