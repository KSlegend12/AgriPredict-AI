from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from backend.config import ALLOWED_CROPS, MAHARASHTRA_DISTRICTS

def _normalize_district(v: str) -> str:
    cleaned = v.strip()
    # Case-insensitive match against canonical 36 Maharashtra districts
    for d in MAHARASHTRA_DISTRICTS:
        if d.lower() == cleaned.lower():
            return d
    # Aliases
    aliases = {
        "aurangabad": "Chhatrapati Sambhajinagar",
        "osmanabad": "Dharashiv",
    }
    if cleaned.lower() in aliases:
        return aliases[cleaned.lower()]
    raise ValueError(
        f"Invalid district '{v}'. Must be one of the 36 Maharashtra districts: {', '.join(sorted(MAHARASHTRA_DISTRICTS.keys()))}"
    )

def _normalize_season(v: str) -> str:
    cleaned = v.strip().capitalize()
    valid_seasons = ["Kharif", "Rabi", "Summer"]
    if cleaned not in valid_seasons:
        raise ValueError(f"Invalid season '{v}'. Must be one of: {', '.join(valid_seasons)}")
    return cleaned

class CropRecommendRequest(BaseModel):
    district: str = Field(..., json_schema_extra={"example": "Pune"})
    season: str = Field(..., json_schema_extra={"example": "Kharif"})
    temperature: float = Field(..., ge=0, le=55, json_schema_extra={"example": 27.0})
    rainfall: float = Field(..., ge=0, le=5000, json_schema_extra={"example": 650.0})
    humidity: float = Field(..., ge=0, le=100, json_schema_extra={"example": 70.0})
    wind_speed: Optional[float] = Field(12.0, ge=0, le=100)
    soil_ph: Optional[float] = Field(None, ge=3.0, le=11.0, json_schema_extra={"example": 6.5})
    nitrogen: Optional[float] = Field(None, ge=0, le=400, json_schema_extra={"example": 80.0})
    phosphorus: Optional[float] = Field(None, ge=0, le=300, json_schema_extra={"example": 45.0})
    potassium: Optional[float] = Field(None, ge=0, le=500, json_schema_extra={"example": 60.0})
    soil_moisture: Optional[float] = Field(None, ge=0, le=100, json_schema_extra={"example": 62.0})
    irrigation: bool = Field(True)
    fertilizer_usage: float = Field(150.0, ge=0, le=600)

    @field_validator("district")
    def validate_district(cls, v):
        return _normalize_district(v)

    @field_validator("season")
    def validate_season(cls, v):
        return _normalize_season(v)

class YieldPredictRequest(BaseModel):
    district: str = Field(..., json_schema_extra={"example": "Akola"})
    crop: str = Field(..., json_schema_extra={"example": "Cotton"})
    target_year: int = Field(2026, ge=2020, le=2035)
    season: str = Field(..., json_schema_extra={"example": "Kharif"})
    temperature: float = Field(..., ge=0, le=55, json_schema_extra={"example": 28.0})
    rainfall: float = Field(..., ge=0, le=5000, json_schema_extra={"example": 800.0})
    humidity: float = Field(..., ge=0, le=100, json_schema_extra={"example": 68.0})
    wind_speed: Optional[float] = Field(12.0, ge=0, le=100)
    soil_ph: Optional[float] = Field(None, ge=3.0, le=11.0, json_schema_extra={"example": 7.5})
    nitrogen: Optional[float] = Field(None, ge=0, le=400, json_schema_extra={"example": 160.0})
    phosphorus: Optional[float] = Field(None, ge=0, le=300, json_schema_extra={"example": 22.0})
    potassium: Optional[float] = Field(None, ge=0, le=500, json_schema_extra={"example": 310.0})
    soil_moisture: Optional[float] = Field(None, ge=0, le=100, json_schema_extra={"example": 60.0})
    irrigation: bool = Field(True)
    fertilizer_usage: float = Field(150.0, ge=0, le=600)
    cultivated_area: float = Field(1.0, ge=0.1, le=500)

    @field_validator("crop")
    def validate_crop(cls, v):
        formatted = v.strip().capitalize()
        if formatted not in ALLOWED_CROPS:
            raise ValueError(f"Crop must be one of strictly: {', '.join(ALLOWED_CROPS)}. AgriPredict-AI is strictly dedicated to Vidarbha Cotton.")
        return formatted

    @field_validator("district")
    def validate_district(cls, v):
        return _normalize_district(v)

    @field_validator("season")
    def validate_season(cls, v):
        return _normalize_season(v)


# ---------------------------------------------------------------------------
# Cotton Yield Prediction — Vidarbha-specific schema
# ---------------------------------------------------------------------------
VIDARBHA_DISTRICTS = Literal[
    "Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"
]


class CottonYieldPredictRequest(BaseModel):
    """Request for a verified historical cotton-yield prediction.

    The backend derives the model feature row from verified panels;
    the frontend does not submit synthetic weather or lag values.
    Supports opt-in model versions:
    - 'production' (default validated model, 1997-2024 canonical features)
    - 'candidate_six_district_dar_deficit_heat_thresh' (Phase 2 Decoupled Agronomic Ridge with Deficit & Heat Thresh, 6 districts)
    - 'candidate_six_district_thermal' (Six-District Thermal Ridge candidate model)
    - 'candidate_six_district_decoupled_agronomic' (Six-District Decoupled Agronomic Ridge candidate model)
    - 'candidate_physiological_ridge_a100' (Ridge Delta Rolling with 9 physiological features, best CV MAE: 101.69 kg/ha)
    - 'candidate_repaired_synth' (Ridge Delta with fold-isolated repaired biophysical synthetic augmentation)
    - 'candidate_delta_rolling' (Ridge Delta Rolling with biophysical agronomic ratios)
    - 'candidate_regularized_ensemble' (Multi-sensor hybrid Ridge + ExtraTrees with NASA SMAP, 2018-2024)
    - 'candidate_satellite_smap' (experimental NASA SMAP soil moisture candidate, 2018-2024)
    - 'candidate_optimized' (leakage-safe sample-weighted candidate)
    - 'candidate_synthetic' (100% synthetic-augmented candidate)
    """

    district: VIDARBHA_DISTRICTS = Field(..., json_schema_extra={"example": "Akola"})
    target_year: int = Field(..., ge=1997, le=2024, json_schema_extra={"example": 2024})
    model_version: Optional[str] = Field("production", json_schema_extra={"example": "production"})

    model_config = {"json_schema_extra": {
        "example": {
            "district": "Akola",
            "target_year": 2024,
            "model_version": "production"
        }
    }}
