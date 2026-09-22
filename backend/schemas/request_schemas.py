from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from backend.config import ALLOWED_CROPS

class CropRecommendRequest(BaseModel):
    district: str = Field(..., example="Pune")
    season: str = Field(..., example="Kharif")
    temperature: float = Field(..., ge=0, le=55, example=27.0)
    rainfall: float = Field(..., ge=0, le=5000, example=650.0)
    humidity: float = Field(..., ge=0, le=100, example=70.0)
    wind_speed: Optional[float] = Field(12.0, ge=0, le=100)
    soil_ph: float = Field(..., ge=3.0, le=11.0, example=6.5)
    nitrogen: float = Field(..., ge=0, le=400, example=80.0)
    phosphorus: float = Field(..., ge=0, le=300, example=45.0)
    potassium: float = Field(..., ge=0, le=300, example=60.0)
    soil_moisture: float = Field(..., ge=0, le=100, example=62.0)
    irrigation: bool = Field(True)
    fertilizer_usage: float = Field(150.0, ge=0, le=600)

class YieldPredictRequest(BaseModel):
    district: str = Field(..., example="Pune")
    crop: str = Field(..., example="Tomato")
    target_year: int = Field(2026, ge=2020, le=2035)
    season: str = Field(..., example="Kharif")
    temperature: float = Field(..., ge=0, le=55, example=27.0)
    rainfall: float = Field(..., ge=0, le=5000, example=650.0)
    humidity: float = Field(..., ge=0, le=100, example=70.0)
    wind_speed: Optional[float] = Field(12.0, ge=0, le=100)
    soil_ph: float = Field(..., ge=3.0, le=11.0, example=6.5)
    nitrogen: float = Field(..., ge=0, le=400, example=80.0)
    phosphorus: float = Field(..., ge=0, le=300, example=45.0)
    potassium: float = Field(..., ge=0, le=300, example=60.0)
    soil_moisture: float = Field(..., ge=0, le=100, example=62.0)
    irrigation: bool = Field(True)
    fertilizer_usage: float = Field(150.0, ge=0, le=600)
    cultivated_area: float = Field(1.0, ge=0.1, le=500)

    @field_validator("crop")
    def validate_crop(cls, v):
        formatted = v.strip().capitalize()
        if formatted not in ALLOWED_CROPS:
            raise ValueError(f"Crop must be one of strictly: {', '.join(ALLOWED_CROPS)}")
        return formatted


# ---------------------------------------------------------------------------
# Cotton Yield Prediction — Vidarbha-specific schema
# ---------------------------------------------------------------------------
VIDARBHA_DISTRICTS = Literal[
    "Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim", "Yavatmal"
]


class CottonYieldPredictRequest(BaseModel):
    """Request for a verified historical cotton-yield prediction.

    The backend derives the complete 36-feature model row from the
    authoritative Vidarbha cotton panel; the frontend does not submit
    synthetic weather or lag values.
    """

    district: VIDARBHA_DISTRICTS = Field(..., example="Akola")
    target_year: int = Field(..., ge=1997, le=2024, example=2024)

    model_config = {"json_schema_extra": {
        "example": {
            "district": "Akola",
            "target_year": 2024
        }
    }}
