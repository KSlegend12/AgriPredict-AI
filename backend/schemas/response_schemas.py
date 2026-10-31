"""
Authoritative Pydantic V2 response schemas for AgriPredict-AI.

These models define and validate the API response contracts across:
- Districts and crop metadata
- Weather telemetry and climatological baselines
- Crop recommendation and multi-factor suitability scores
- Cotton yield predictions, confidence bounds, and local SHAP explanations
- Future forecasting multi-year horizons (2027-2031)
- Query history audit trail
- Health and readiness status
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Union

# ===========================================================================
# 1. DISTRICTS & METADATA
# ===========================================================================

class DistrictItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., description="Canonical district name")
    region: str = Field(..., description="Agro-climatic division (e.g. Vidarbha, Western Maharashtra)")
    lat: float = Field(..., description="Latitude coordinate")
    lon: float = Field(..., description="Longitude coordinate")
    avg_rainfall: float = Field(..., description="Annual normal precipitation in mm")

class DistrictsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = Field("success", description="Status indicator")
    state: str = Field("Maharashtra", description="State name")
    total_districts: int = Field(..., description="Total count of supported districts")
    allowed_crops: List[str] = Field(..., description="Supported horticulture crops")
    districts: List[DistrictItem] = Field(..., description="List of district metadata")


# ===========================================================================
# 2. WEATHER TELEMETRY
# ===========================================================================

class WeatherData(BaseModel):
    model_config = ConfigDict(extra="allow")
    district: str
    region: str
    temperature: float = Field(..., description="Air temperature in °C")
    feels_like: float = Field(..., description="Apparent temperature in °C")
    humidity: int = Field(..., description="Relative humidity percentage")
    rainfall: float = Field(..., description="District seasonal/annual normal rainfall in mm")
    precipitation_live_mm: Optional[float] = Field(0.0, description="Current live precipitation rate in mm")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    condition: str = Field(..., description="General weather category")
    description: str = Field(..., description="Descriptive condition label")
    is_live_api: Optional[bool] = Field(False, description="Whether data is from live telemetry")
    provider: Optional[str] = Field(None, description="Weather provider (Open-Meteo, OpenWeatherMap, Climatology)")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture index percentage")
    soil_ph: Optional[float] = Field(None, description="Soil pH value")

class WeatherResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    data: WeatherData


# ===========================================================================
# 3. CROP RECOMMENDATION & SUITABILITY
# ===========================================================================

class FactorScores(BaseModel):
    model_config = ConfigDict(extra="allow")
    temperature: float
    rainfall: float
    soil: float
    humidity: float
    season: float

class CropRecommendationItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    crop: str = Field(..., description="Crop name (Tomato, Onion, Sugarcane)")
    icon: str = Field(..., description="Display icon emoji")
    suitability_percentage: float = Field(..., description="Composite suitability score (0-100%)")
    predicted_yield_ha: float = Field(..., description="Estimated yield in tonnes/ha")
    yield_range: str = Field(..., description="Estimated confidence range string")
    confidence_score: float = Field(..., description="Model confidence score")
    why_recommendation: str = Field(..., description="Biophysical reasoning summary")
    advisories: List[str] = Field(default_factory=list, description="Actionable agronomic advisories")
    factor_scores: FactorScores
    rank: int = Field(..., description="Suitability ranking (1 is top)")

class CropRecommendResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    is_real_model: bool
    district: str
    season: str
    recommended_crop: str
    recommendations: List[CropRecommendationItem]


# ===========================================================================
# 4. YIELD PREDICTION
# ===========================================================================

class YieldTrendItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    year: str
    yield_: float = Field(..., alias="yield")
    type: str

class YieldPredictResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    is_real_model: Optional[bool] = True
    crop: str
    district: str
    target_year: int
    season: str
    predicted_yield_ha: float
    total_production_tonnes: Optional[float] = None
    yield_range: Optional[str] = None
    historical_avg_ha: Optional[float] = None
    percentage_change: Optional[float] = None
    trend: Optional[List[Dict[str, Any]]] = None



# ===========================================================================
# 5. COTTON YIELD PREDICTION & XAI
# ===========================================================================

class PredictionInterval(BaseModel):
    model_config = ConfigDict(extra="allow")
    confidence_level: Optional[str] = None
    lower_bound_kg_per_ha: Optional[float] = None
    upper_bound_kg_per_ha: Optional[float] = None
    interval_range_kg_per_ha: Optional[float] = None

class InfluentialFeature(BaseModel):
    model_config = ConfigDict(extra="allow")
    feature: str
    display_name: str
    value: Optional[float] = None
    contribution_kg_ha: float
    direction: str

class ExplanationData(BaseModel):
    model_config = ConfigDict(extra="allow")
    available: bool = True
    base_value_kg_ha: Optional[float] = None
    top_influential_features: List[InfluentialFeature] = Field(default_factory=list)

class CottonPredictResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    predicted_yield_kg_ha: float = Field(..., description="Point estimate in kg/ha lint")
    model_name: str = Field(..., description="Internal estimator pipeline name")
    model_version: str = Field(..., description="Registered version key")
    prediction_status: Optional[str] = None
    prediction_input: Optional[Dict[str, Any]] = None
    prediction_interval: Optional[PredictionInterval] = None
    explanation: Optional[ExplanationData] = None
    validation_metrics: Optional[Dict[str, Any]] = None
    holdout_2024_metrics: Optional[Dict[str, Any]] = None
    satellite_features_used: Optional[bool] = False


# ===========================================================================
# 6. FUTURE FORECASTING
# ===========================================================================

class FutureForecastItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    year: int
    predicted_yield_kg_ha: float
    uncertainty_lower_kg_ha: float
    uncertainty_upper_kg_ha: float
    confidence_level: Optional[str] = None

class FutureForecastDistrictsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    districts: List[str]
    forecast_years: List[int]
    scenarios: List[str]

class FutureForecastResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    district: str
    origin_year: int = 2024
    forecast_years: List[int] = Field(default_factory=lambda: [2027, 2028, 2029, 2030, 2031])
    scenarios: Dict[str, List[FutureForecastItem]]
    data_provenance: Optional[Dict[str, Any]] = None


# ===========================================================================
# 7. PREDICTION HISTORY
# ===========================================================================

class HistoryItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: int
    timestamp: str
    district: str
    crop_type: Optional[str] = None
    recommended_crop: Optional[str] = None
    predicted_yield: Optional[float] = None
    season: Optional[str] = None
    model_version: Optional[str] = None
    model_type: Optional[str] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    input_parameters: Dict[str, Any] = Field(default_factory=dict)

class HistoryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    total: int
    history: List[HistoryItem]


# ===========================================================================
# 8. COTTON METADATA & GLOBAL EXPLANATIONS
# ===========================================================================

class CottonDistrictRecentYear(BaseModel):
    model_config = ConfigDict(extra="allow")
    year: int
    yield_kg_ha: float

class CottonDistrictMeta(BaseModel):
    model_config = ConfigDict(extra="allow")
    district: str
    years_available: int
    year_range: str
    historical_mean_kg_ha: float
    historical_min_kg_ha: float
    historical_max_kg_ha: float
    recent_5yr_mean_kg_ha: float
    recent_5yr: List[CottonDistrictRecentYear]

class CottonDistrictsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    geographic_scope: str
    crop: str
    total_districts: int
    districts: List[CottonDistrictMeta]
    supported_prediction_years: List[int]

class CottonModelInfoResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    model_name: str
    crop: str
    geographic_scope: str
    training_years: str
    num_training_rows: int
    validation_period: Optional[str] = None
    validation_metrics: Optional[Dict[str, Any]] = None
    holdout_2024_metrics: Optional[Dict[str, Any]] = None
    total_features: int
    feature_cols: List[str]
    top_10_features: List[Dict[str, Any]]
    global_shap_importance: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    all_models_comparison: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    is_model_loaded: bool
    supported_prediction_years: List[int]

class CottonXaiGlobalResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = "success"
    methodology: str
    model_name: str
    training_period: str
    sample_count: int
    base_value_kg_ha: float
    total_features: int
    category_summary: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    global_feature_importance: List[Dict[str, Any]]
    top_10_features: List[Dict[str, Any]]

# ===========================================================================
# 9. HEALTH & READINESS
# ===========================================================================

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str
    app_name: str
    version: str
    geographic_scope: str
    modules: Dict[str, Any]

class ReadyResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    ready: bool
    models: Dict[str, Any]

