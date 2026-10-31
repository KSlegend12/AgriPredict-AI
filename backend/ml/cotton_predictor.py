"""
Cotton Yield Predictor for Vidarbha, Maharashtra.

Uses the validated GradientBoosting pipeline trained on 1997-2023 data.
Final holdout year: 2024.
Validation: 2011-2023 expanding-window temporal cross-validation.

Provides:
1. Point prediction (kg/ha)
2. Real local feature explanations using SHAP
3. Human-readable feature mapping
4. District historical benchmarks
5. Validation and transparency metadata
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import shap


# =========================================================
# PATH RESOLUTION
# =========================================================

_HERE = os.path.dirname(os.path.abspath(__file__))
_ML_ROOT = _HERE
_ARTIFACTS = os.path.join(_ML_ROOT, "artifacts")

# IMPORTANT:
# This is the validated final model trained on 1997-2023.
MODEL_PATH = os.path.join(
    _ARTIFACTS,
    "final_model.pkl"
)

METADATA_PATH = os.path.join(
    _ARTIFACTS,
    "model_metadata.json"
)

# Experimental Candidate Model (Synthetic-Augmented)
CANDIDATE_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "synthetic_expansion",
    "artifacts"
)
CANDIDATE_MODEL_PATH = os.path.join(
    CANDIDATE_ARTIFACTS,
    "GradientBoosting_Synth_100pct.pkl"
)
CANDIDATE_METADATA_PATH = os.path.join(
    CANDIDATE_ARTIFACTS,
    "candidate_metadata.json"
)

# Optimized Model (Leakage-Safe Sample-Weighted sw=0.05)
OPTIMIZED_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "model_optimization",
    "artifacts"
)
OPTIMIZED_MODEL_PATH = os.path.join(
    OPTIMIZED_ARTIFACTS,
    "GradientBoosting_Optimized_sw005.pkl"
)
OPTIMIZED_METADATA_PATH = os.path.join(
    OPTIMIZED_ARTIFACTS,
    "optimized_candidate_metadata.json"
)

# Candidate Satellite SMAP Model (NASA SMAP Level-4 Soil Moisture)
SATELLITE_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "satellite_soil_moisture_expansion",
    "artifacts"
)
SATELLITE_MODEL_PATH = os.path.join(
    SATELLITE_ARTIFACTS,
    "GradientBoosting_Satellite_SMAP.pkl"
)
SATELLITE_METADATA_PATH = os.path.join(
    SATELLITE_ARTIFACTS,
    "satellite_candidate_metadata.json"
)

SATELLITE_SMAP_FEATURES = [
    "sm_surface_kharif_mean",
    "sm_rootzone_kharif_mean",
    "sm_surface_monsoon_mean",
    "sm_rootzone_monsoon_mean",
    "sm_surface_kharif_mean_lag1",
    "sm_rootzone_kharif_mean_lag1",
]

# Candidate 1: Ridge Delta Rolling (3-Year Rolling Anchor + Biophysical Residual)
DELTA_ROLLING_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "performance_optimization",
    "artifacts"
)
DELTA_ROLLING_MODEL_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "Ridge_Delta_Rolling_Agronomic.pkl"
)
DELTA_ROLLING_METADATA_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "delta_rolling_candidate_metadata.json"
)

# Candidate 2: Hybrid Regularized Multi-Sensor Ensemble (Ridge 55% + ExtraTrees 45%)
REGULARIZED_ENSEMBLE_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "performance_optimization",
    "artifacts"
)
REGULARIZED_ENSEMBLE_MODEL_PATH = os.path.join(
    REGULARIZED_ENSEMBLE_ARTIFACTS,
    "Ensemble_Ridge_ExtraTrees_SMAP.pkl"
)
REGULARIZED_ENSEMBLE_METADATA_PATH = os.path.join(
    REGULARIZED_ENSEMBLE_ARTIFACTS,
    "regularized_ensemble_candidate_metadata.json"
)

# Candidate 3: Repaired Biophysical Synthetic Ridge Delta (Conservative sw=0.10)
REPAIRED_SYNTH_MODEL_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "Ridge_Delta_Repaired_Synth_sw010.pkl"
)
REPAIRED_SYNTH_METADATA_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "repaired_synth_candidate_metadata.json"
)

# Candidate 4: Ridge Delta Rolling with Physiological Features (alpha=100)
PHYSIOLOGICAL_RIDGE_MODEL_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "Ridge_Delta_Rolling_Physiological_a100.pkl"
)
PHYSIOLOGICAL_RIDGE_METADATA_PATH = os.path.join(
    DELTA_ROLLING_ARTIFACTS,
    "physiological_ridge_candidate_metadata.json"
)

# Candidate 5: Six-District Ridge Delta Rolling with Physiological Features (alpha=100, excludes Yavatmal)
SIX_DISTRICT_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "six_district_optimization",
    "artifacts"
)
SIX_DISTRICT_MODEL_PATH = os.path.join(
    SIX_DISTRICT_ARTIFACTS,
    "Ridge_Delta_Rolling_SixDistricts_Physiological.pkl"
)
SIX_DISTRICT_METADATA_PATH = os.path.join(
    SIX_DISTRICT_ARTIFACTS,
    "six_district_candidate_metadata.json"
)

# Candidate 6: Six-District Ridge Delta Rolling with Thermal Features (alpha=100, excludes Yavatmal)
SIX_DISTRICT_THERMAL_MODEL_PATH = os.path.join(
    SIX_DISTRICT_ARTIFACTS,
    "Ridge_Delta_Rolling_SixDistricts_Thermal.pkl"
)
SIX_DISTRICT_THERMAL_METADATA_PATH = os.path.join(
    SIX_DISTRICT_ARTIFACTS,
    "six_district_thermal_candidate_metadata.json"
)

# Candidate 7: Six-District Decoupled Agronomic Ridge (alpha=100, excludes Yavatmal)
DECOUPLED_AGRONOMIC_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "cotton_yield_regime_fix",
    "artifacts"
)
DECOUPLED_AGRONOMIC_MODEL_PATH = os.path.join(
    DECOUPLED_AGRONOMIC_ARTIFACTS,
    "Ridge_Delta_Rolling_SixDistricts_Decoupled_Agronomic.pkl"
)
DECOUPLED_AGRONOMIC_METADATA_PATH = os.path.join(
    DECOUPLED_AGRONOMIC_ARTIFACTS,
    "decoupled_agronomic_candidate_metadata.json"
)

# Candidate 8: Six-District Decoupled Agronomic Ridge with Deficit & Heat Thresh (alpha=75, excludes Yavatmal)
DECOUPLED_DEFICIT_HEAT_ARTIFACTS = os.path.join(
    _ML_ROOT,
    "experiments",
    "phase2_deep_scientific_optimization_2026",
    "artifacts"
)
DECOUPLED_DEFICIT_HEAT_MODEL_PATH = os.path.join(
    DECOUPLED_DEFICIT_HEAT_ARTIFACTS,
    "Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh.pkl"
)
DECOUPLED_DEFICIT_HEAT_METADATA_PATH = os.path.join(
    DECOUPLED_DEFICIT_HEAT_ARTIFACTS,
    "metadata_Decoupled_Agronomic_Ridge_Deficit_HeatThresh_a75.json"
)

AGRONOMIC_ENGINEERED_FEATURES = [
    "diurnal_range_kharif",
    "rain_intensity_kharif",
    "dry_heat_compound",
    "single_day_deluge_ratio",
    "yield_momentum",
    "yield_ratio_to_rolling3",
]

PHYSIOLOGICAL_ENGINEERED_FEATURES = [
    "rain_gentleness_ratio",
    "heavy_rain_fraction",
    "extreme_heat_ratio",
    "diurnal_range_kharif",
    "single_day_deluge_ratio",
    "drought_buffer_index",
    "yield_momentum",
    "yield_excess_over_rolling3",
    "yield_ratio_to_rolling3",
]

ENSEMBLE_SMAP_FEATURES = [
    "sm_surface_kharif_mean",
    "sm_rootzone_kharif_mean",
    "sm_surface_monsoon_mean",
    "sm_rootzone_monsoon_mean",
    "sm_surface_kharif_max",
    "sm_rootzone_kharif_max",
]

from backend.config import CANONICAL_COTTON_DATASET_PATH
from backend.ml.xai_engine import xai_engine

# Legacy/global feature importance file.
# This is kept for compatibility with the existing project.
FI_PATH = os.path.join(
    _ARTIFACTS,
    "feature_importance.json"
)

DATA_PATH = str(CANONICAL_COTTON_DATASET_PATH)


# =========================================================
# VALID DISTRICTS
# =========================================================

VALID_DISTRICTS = [
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim"
]


# =========================================================
# AUTHORITATIVE MODEL FEATURE SCHEMA
# =========================================================

FEATURE_COLS = [
    "district",
    "cotton_area_000ha",

    "tmax_annual_mean_c",
    "tmax_monsoon_mean_c",
    "tmax_kharif_mean_c",
    "tmax_max_c",
    "tmax_hot_days_ge35_kharif",

    "tmin_annual_mean_c",
    "tmin_monsoon_mean_c",
    "tmin_kharif_mean_c",
    "tmin_min_c",

    "rainfall_annual_mm",
    "rainy_days_annual",
    "heavy_rain_days_annual",
    "rainfall_max_1day_annual_mm",
    "max_5day_rain_annual_mm",
    "max_dry_spell_annual_days",

    "rainfall_monsoon_mm",
    "rainy_days_monsoon",
    "heavy_rain_days_monsoon",
    "rainfall_max_1day_monsoon_mm",
    "max_5day_rain_monsoon_mm",
    "max_dry_spell_monsoon_days",

    "rainfall_kharif_mm",
    "rainy_days_kharif",
    "heavy_rain_days_kharif",
    "rainfall_max_1day_kharif_mm",
    "max_5day_rain_kharif_mm",
    "max_dry_spell_kharif_days",

    "previous_year_yield_kg_ha",
    "previous_2year_yield_kg_ha",
    "rolling_3yr_yield_mean_kg_ha",

    "rainfall_monsoon_mm_district_anomaly",
    "rainfall_kharif_mm_district_anomaly",
    "tmax_kharif_mean_c_district_anomaly",
    "tmin_kharif_mean_c_district_anomaly",
]

SATELLITE_FEATURE_COLS = FEATURE_COLS + SATELLITE_SMAP_FEATURES
DELTA_ROLLING_FEATURE_COLS = FEATURE_COLS + AGRONOMIC_ENGINEERED_FEATURES
PHYSIOLOGICAL_FEATURE_COLS = FEATURE_COLS + PHYSIOLOGICAL_ENGINEERED_FEATURES
THERMAL_ENGINEERED_FEATURES = ["extreme_heat_ratio", "diurnal_range_kharif"]
THERMAL_FEATURE_COLS = FEATURE_COLS + THERMAL_ENGINEERED_FEATURES
DECOUPLED_AGRONOMIC_ENGINEERED_FEATURES = [
    "extreme_heat_ratio",
    "diurnal_range_kharif",
    "excess_rain_kharif",
    "continuous_wetness_risk"
]
DECOUPLED_AGRONOMIC_FEATURE_COLS = [c for c in FEATURE_COLS if c != "rolling_3yr_yield_mean_kg_ha"] + DECOUPLED_AGRONOMIC_ENGINEERED_FEATURES
DECOUPLED_DEFICIT_HEAT_ENGINEERED_FEATURES = [
    "extreme_heat_ratio",
    "diurnal_range_kharif",
    "excess_rain_kharif",
    "continuous_wetness_risk",
    "rain_deficit_kharif",
    "hot_days_thresh10",
]
DECOUPLED_DEFICIT_HEAT_FEATURE_COLS = [c for c in FEATURE_COLS if c != "rolling_3yr_yield_mean_kg_ha"] + DECOUPLED_DEFICIT_HEAT_ENGINEERED_FEATURES
REGULARIZED_ENSEMBLE_FEATURE_COLS = FEATURE_COLS + AGRONOMIC_ENGINEERED_FEATURES + ENSEMBLE_SMAP_FEATURES


# =========================================================
# HUMAN-READABLE FEATURE NAMES
# =========================================================

HUMAN_READABLE_NAMES = {
    # NASA SMAP satellite features
    "sm_surface_kharif_mean":
        "Kharif Surface Soil Moisture (0-5 cm, m³/m³)",

    "sm_rootzone_kharif_mean":
        "Kharif Root Zone Soil Moisture (0-100 cm, m³/m³)",

    "sm_surface_monsoon_mean":
        "Monsoon Surface Soil Moisture (0-5 cm, m³/m³)",

    "sm_rootzone_monsoon_mean":
        "Monsoon Root Zone Soil Moisture (0-100 cm, m³/m³)",

    "sm_surface_kharif_mean_lag1":
        "Prior-Year Kharif Surface Soil Moisture (m³/m³)",

    "sm_rootzone_kharif_mean_lag1":
        "Prior-Year Kharif Root Zone Soil Moisture (m³/m³)",

    "cotton_area_000ha":
        "Cotton Sown Area (000 ha)",

    "tmax_annual_mean_c":
        "Annual Mean Max Temperature (°C)",

    "tmax_monsoon_mean_c":
        "Monsoon Mean Max Temperature (°C)",

    "tmax_kharif_mean_c":
        "Average Kharif Maximum Temperature (°C)",

    "tmax_max_c":
        "Peak Maximum Temperature (°C)",

    "tmax_hot_days_ge35_kharif":
        "Hot Days (≥35°C) in Kharif",

    "tmin_annual_mean_c":
        "Annual Mean Min Temperature (°C)",

    "tmin_monsoon_mean_c":
        "Monsoon Mean Min Temperature (°C)",

    "tmin_kharif_mean_c":
        "Average Kharif Minimum Temperature (°C)",

    "tmin_min_c":
        "Minimum Season Temperature (°C)",

    "rainfall_annual_mm":
        "Annual Total Rainfall (mm)",

    "rainy_days_annual":
        "Annual Rainy Days",

    "heavy_rain_days_annual":
        "Heavy Rain Days (Annual)",

    "rainfall_max_1day_annual_mm":
        "1-Day Max Rainfall (mm)",

    "max_5day_rain_annual_mm":
        "5-Day Max Rainfall (mm)",

    "max_dry_spell_annual_days":
        "Maximum Annual Dry Spell (Days)",

    "rainfall_monsoon_mm":
        "Monsoon Rainfall (mm)",

    "rainy_days_monsoon":
        "Monsoon Rainy Days",

    "heavy_rain_days_monsoon":
        "Monsoon Heavy Rain Days",

    "rainfall_max_1day_monsoon_mm":
        "Monsoon 1-Day Max Rainfall (mm)",

    "max_5day_rain_monsoon_mm":
        "Monsoon 5-Day Max Rainfall (mm)",

    "max_dry_spell_monsoon_days":
        "Maximum Monsoon Dry Spell (Days)",

    "rainfall_kharif_mm":
        "Kharif Rainfall (mm)",

    "rainy_days_kharif":
        "Kharif Rainy Days",

    "heavy_rain_days_kharif":
        "Kharif Heavy Rain Days",

    "rainfall_max_1day_kharif_mm":
        "Kharif 1-Day Max Rainfall (mm)",

    "max_5day_rain_kharif_mm":
        "Kharif 5-Day Max Rainfall (mm)",

    "max_dry_spell_kharif_days":
        "Maximum Kharif Dry Spell (Days)",

    "previous_year_yield_kg_ha":
        "Previous Year Cotton Yield (kg/ha)",

    "previous_2year_yield_kg_ha":
        "Previous 2-Year Cotton Yield (kg/ha)",

    "rolling_3yr_yield_mean_kg_ha":
        "3-Year Rolling Average Cotton Yield (kg/ha)",

    "rainfall_monsoon_mm_district_anomaly":
        "Monsoon Rainfall Anomaly (mm)",

    "rainfall_kharif_mm_district_anomaly":
        "Kharif Rainfall Anomaly (mm)",

    "tmax_kharif_mean_c_district_anomaly":
        "Kharif Max Temperature Anomaly (°C)",

    "tmin_kharif_mean_c_district_anomaly":
        "Kharif Min Temperature Anomaly (°C)",

    "district_Akola":
        "District: Akola",

    "district_Amravati":
        "District: Amravati",

    "district_Buldhana":
        "District: Buldhana",

    "district_Nagpur":
        "District: Nagpur",

    "district_Wardha":
        "District: Wardha",

    "district_Washim":
        "District: Washim",

    "district_Yavatmal":
        "District: Yavatmal",

    # Engineered Physiological Features
    "rain_gentleness_ratio":
        "Kharif Rain Gentleness Ratio (days/100mm)",

    "heavy_rain_fraction":
        "Kharif Heavy Rain Days Fraction",

    "extreme_heat_ratio":
        "Extreme Heat Days Fraction (Kharif)",

    "drought_buffer_index":
        "Drought Buffer Index (mm/dry day)",

    "yield_momentum":
        "2-Year Yield Momentum (kg/ha)",

    "yield_excess_over_rolling3":
        "Yield Excess Over 3-Yr Rolling Mean (kg/ha)",

    "yield_ratio_to_rolling3":
        "Yield Ratio to 3-Year Rolling Mean",

    "diurnal_range_kharif":
        "Kharif Diurnal Temperature Range (°C)",

    "single_day_deluge_ratio":
        "Single-Day Deluge Rainfall Fraction",

    "excess_rain_kharif":
        "Excess Kharif Rain Above 800mm (x100mm)",

    "continuous_wetness_risk":
        "Continuous Wetness Risk Index",

    "rain_deficit_kharif":
        "Kharif Rainfall Deficit Below 750mm (x100mm)",

    "hot_days_thresh10":
        "Extreme Heat Days Exceeding 10 Days (x10 days)",
}


# =========================================================
# FEATURE AVAILABILITY
# =========================================================

FEATURE_AVAILABILITY = {

    "realtime_inputs": [
        col
        for col in FEATURE_COLS
        if "yield" not in col and col != "district"
    ],

    "lag_features_require_prior_year_data": [
        "previous_year_yield_kg_ha",
        "previous_2year_yield_kg_ha",
        "rolling_3yr_yield_mean_kg_ha",
    ]
}


# =========================================================
# COTTON YIELD PREDICTOR
# =========================================================

class CottonYieldPredictor:
    """
    Serves the validated GradientBoosting cotton yield model
    with local SHAP explanations.
    """

    def __init__(self):

        self.pipeline = None
        self.preprocessor = None
        self.model = None
        self.explainer = None

        self.metadata = {}
        self.feature_importance = []
        self.historical_df = None

        self.is_loaded = False

        # Controlled candidate model attributes
        self.candidate_pipeline = None
        self.candidate_preprocessor = None
        self.candidate_model = None
        self.candidate_explainer = None
        self.candidate_metadata = {}
        self.candidate_is_loaded = False

        # Controlled optimized candidate model attributes
        self.opt_pipeline = None
        self.opt_preprocessor = None
        self.opt_model = None
        self.opt_explainer = None
        self.opt_metadata = {}
        self.opt_is_loaded = False

        # Controlled satellite candidate model attributes
        self.satellite_pipeline = None
        self.satellite_preprocessor = None
        self.satellite_model = None
        self.satellite_explainer = None
        self.satellite_metadata = {}
        self.satellite_is_loaded = False

        # Controlled Ridge Delta Rolling model attributes
        self.delta_pipeline = None
        self.delta_metadata = {}
        self.delta_is_loaded = False

        # Controlled Regularized Ensemble model attributes
        self.reg_ensemble_dict = None
        self.reg_ensemble_metadata = {}
        self.reg_ensemble_is_loaded = False

        # Controlled Physiological Ridge (alpha=100) model attributes
        self.phys_ridge_pipeline = None
        self.phys_ridge_metadata = {}
        self.phys_ridge_is_loaded = False

        # Controlled Six-District Physiological Ridge candidate model attributes
        self.six_dist_pipeline = None
        self.six_dist_metadata = {}
        self.six_dist_is_loaded = False

        # Controlled Six-District Thermal-Only Ridge candidate model attributes
        self.six_dist_thermal_pipeline = None
        self.six_dist_thermal_metadata = {}
        self.six_dist_thermal_is_loaded = False

        # Controlled Six-District Decoupled Deficit Heat Thresh Ridge candidate model attributes
        self.decoupled_deficit_heat_pipeline = None
        self.decoupled_deficit_heat_metadata = {}
        self.decoupled_deficit_heat_is_loaded = False

        self._load()


    # =====================================================
    # LOAD MODEL + METADATA
    # =====================================================

    def _load(self):

        try:

            # ---------------------------------------------
            # Load validated final model
            # ---------------------------------------------

            if not os.path.exists(MODEL_PATH):

                raise FileNotFoundError(
                    f"Validated model not found: {MODEL_PATH}"
                )

            self.pipeline = joblib.load(MODEL_PATH)

            # Validate pipeline structure
            if not hasattr(self.pipeline, "named_steps"):

                raise ValueError(
                    "final_model.pkl is not a valid sklearn Pipeline."
                )

            if "preprocessor" not in self.pipeline.named_steps:

                raise ValueError(
                    "Pipeline does not contain 'preprocessor' step."
                )

            if "model" not in self.pipeline.named_steps:

                raise ValueError(
                    "Pipeline does not contain 'model' step."
                )

            self.preprocessor = (
                self.pipeline.named_steps["preprocessor"]
            )

            self.model = (
                self.pipeline.named_steps["model"]
            )


            # ---------------------------------------------
            # SHAP TreeExplainer
            # ---------------------------------------------

            try:

                self.explainer = shap.TreeExplainer(
                    self.model
                )

            except Exception as ex:

                print(
                    f"[Cotton ML] SHAP warning: {ex}"
                )

                self.explainer = None


            # ---------------------------------------------
            # Load metadata
            # ---------------------------------------------

            if os.path.exists(METADATA_PATH):

                with open(
                    METADATA_PATH,
                    "r",
                    encoding="utf-8"
                ) as f:

                    self.metadata = json.load(f)


            # ---------------------------------------------
            # Load optional legacy feature importance
            # ---------------------------------------------

            if os.path.exists(FI_PATH):

                try:

                    with open(
                        FI_PATH,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        self.feature_importance = json.load(f)

                except Exception as ex:

                    print(
                        f"[Cotton ML] Feature importance warning: {ex}"
                    )

                    self.feature_importance = []


            # ---------------------------------------------
            # Load authoritative historical dataset
            # ---------------------------------------------

            if os.path.exists(DATA_PATH):

                self.historical_df = pd.read_csv(
                    DATA_PATH
                )


            # ---------------------------------------------
            # Model successfully loaded
            # ---------------------------------------------

            self.is_loaded = True

            print(
                "[Cotton ML] Validated GradientBoosting "
                "pipeline loaded successfully."
            )

            print(
                f"[Cotton ML] Model path: {MODEL_PATH}"
            )

            print(
                f"[Cotton ML] Training years: "
                f"{self.metadata.get('training_years', 'unknown')}"
            )

            print(
                f"[Cotton ML] Holdout year: "
                f"{self.metadata.get('holdout_year', 'unknown')}"
            )

            # ---------------------------------------------
            # Load controlled candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(CANDIDATE_MODEL_PATH):
                try:
                    self.candidate_pipeline = joblib.load(CANDIDATE_MODEL_PATH)
                    if hasattr(self.candidate_pipeline, "named_steps"):
                        self.candidate_preprocessor = self.candidate_pipeline.named_steps.get("preprocessor")
                        self.candidate_model = self.candidate_pipeline.named_steps.get("model")
                        try:
                            self.candidate_explainer = shap.TreeExplainer(self.candidate_model)
                        except Exception as cand_shap_ex:
                            print(f"[Cotton ML] Candidate SHAP warning: {cand_shap_ex}")
                            self.candidate_explainer = None
                    if os.path.exists(CANDIDATE_METADATA_PATH):
                        with open(CANDIDATE_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.candidate_metadata = json.load(f)
                    self.candidate_is_loaded = True
                    print(
                        f"[Cotton ML] Controlled Candidate model loaded successfully: "
                        f"{self.candidate_metadata.get('model_name', 'GradientBoosting_Synth_100pct')}"
                    )
                except Exception as cand_load_ex:
                    print(f"[Cotton ML] Candidate model loading warning: {cand_load_ex}")
                    self.candidate_is_loaded = False
            else:
                self.candidate_is_loaded = False

            # ---------------------------------------------
            # Load optimized candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(OPTIMIZED_MODEL_PATH):
                try:
                    self.opt_pipeline = joblib.load(OPTIMIZED_MODEL_PATH)
                    if hasattr(self.opt_pipeline, "named_steps"):
                        self.opt_preprocessor = self.opt_pipeline.named_steps.get("preprocessor")
                        self.opt_model = self.opt_pipeline.named_steps.get("model")
                        try:
                            self.opt_explainer = shap.TreeExplainer(self.opt_model)
                        except Exception as opt_shap_ex:
                            print(f"[Cotton ML] Optimized candidate SHAP warning: {opt_shap_ex}")
                            self.opt_explainer = None
                    if os.path.exists(OPTIMIZED_METADATA_PATH):
                        with open(OPTIMIZED_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.opt_metadata = json.load(f)
                    self.opt_is_loaded = True
                    print(
                        f"[Cotton ML] Optimized candidate model loaded successfully: "
                        f"{self.opt_metadata.get('model_name', 'GradientBoosting_Optimized_sw005')}"
                    )
                except Exception as opt_load_ex:
                    print(f"[Cotton ML] Optimized model loading warning: {opt_load_ex}")
                    self.opt_is_loaded = False
            else:
                self.opt_is_loaded = False

            # ---------------------------------------------
            # Load satellite candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(SATELLITE_MODEL_PATH):
                try:
                    self.satellite_pipeline = joblib.load(SATELLITE_MODEL_PATH)
                    if hasattr(self.satellite_pipeline, "named_steps"):
                        self.satellite_preprocessor = self.satellite_pipeline.named_steps.get("preprocessor")
                        self.satellite_model = self.satellite_pipeline.named_steps.get("model")
                        try:
                            self.satellite_explainer = shap.TreeExplainer(self.satellite_model)
                        except Exception as sat_shap_ex:
                            print(f"[Cotton ML] Satellite candidate SHAP warning: {sat_shap_ex}")
                            self.satellite_explainer = None
                    if os.path.exists(SATELLITE_METADATA_PATH):
                        with open(SATELLITE_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.satellite_metadata = json.load(f)
                    self.satellite_is_loaded = True
                    print(
                        f"[Cotton ML] Satellite candidate model loaded successfully: "
                        f"{self.satellite_metadata.get('model_name', 'GradientBoosting_Satellite_SMAP')}"
                    )
                except Exception as sat_load_ex:
                    print(f"[Cotton ML] Satellite model loading warning: {sat_load_ex}")
                    self.satellite_is_loaded = False
            else:
                self.satellite_is_loaded = False

            # ---------------------------------------------
            # Load Ridge Delta Rolling candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(DELTA_ROLLING_MODEL_PATH):
                try:
                    self.delta_pipeline = joblib.load(DELTA_ROLLING_MODEL_PATH)
                    if os.path.exists(DELTA_ROLLING_METADATA_PATH):
                        with open(DELTA_ROLLING_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.delta_metadata = json.load(f)
                    self.delta_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Delta Rolling model loaded successfully: "
                        f"{self.delta_metadata.get('model_name', 'Ridge_Delta_Rolling_Agronomic')}"
                    )
                except Exception as delta_load_ex:
                    print(f"[Cotton ML] Candidate Delta Rolling loading warning: {delta_load_ex}")
                    self.delta_is_loaded = False
            else:
                self.delta_is_loaded = False

            # ---------------------------------------------
            # Load Regularized Ensemble candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(REGULARIZED_ENSEMBLE_MODEL_PATH):
                try:
                    self.reg_ensemble_dict = joblib.load(REGULARIZED_ENSEMBLE_MODEL_PATH)
                    if os.path.exists(REGULARIZED_ENSEMBLE_METADATA_PATH):
                        with open(REGULARIZED_ENSEMBLE_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.reg_ensemble_metadata = json.load(f)
                    self.reg_ensemble_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Regularized Ensemble loaded successfully: "
                        f"{self.reg_ensemble_metadata.get('model_name', 'Ensemble_Ridge_ExtraTrees_SMAP')}"
                    )
                except Exception as ens_load_ex:
                    print(f"[Cotton ML] Candidate Regularized Ensemble loading warning: {ens_load_ex}")
                    self.reg_ensemble_is_loaded = False
            else:
                self.reg_ensemble_is_loaded = False

            # ---------------------------------------------
            # Load Repaired Biophysical Synthetic Candidate model (if present)
            # ---------------------------------------------
            if os.path.exists(REPAIRED_SYNTH_MODEL_PATH):
                try:
                    self.repaired_synth_pipeline = joblib.load(REPAIRED_SYNTH_MODEL_PATH)
                    if os.path.exists(REPAIRED_SYNTH_METADATA_PATH):
                        with open(REPAIRED_SYNTH_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.repaired_synth_metadata = json.load(f)
                    self.repaired_synth_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Repaired Synth model loaded successfully: "
                        f"{self.repaired_synth_metadata.get('model_name', 'Ridge_Delta_Repaired_Synth_sw010')}"
                    )
                except Exception as rep_load_ex:
                    print(f"[Cotton ML] Candidate Repaired Synth loading warning: {rep_load_ex}")
                    self.repaired_synth_is_loaded = False
            else:
                self.repaired_synth_is_loaded = False

            # ---------------------------------------------
            # Load Physiological Ridge Candidate model (alpha=100)
            # ---------------------------------------------
            if os.path.exists(PHYSIOLOGICAL_RIDGE_MODEL_PATH):
                try:
                    self.phys_ridge_pipeline = joblib.load(PHYSIOLOGICAL_RIDGE_MODEL_PATH)
                    if os.path.exists(PHYSIOLOGICAL_RIDGE_METADATA_PATH):
                        with open(PHYSIOLOGICAL_RIDGE_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.phys_ridge_metadata = json.load(f)
                    self.phys_ridge_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Physiological Ridge model loaded successfully: "
                        f"{self.phys_ridge_metadata.get('model_name', 'Ridge_Delta_Rolling_Physiological_a100')}"
                    )
                except Exception as phys_load_ex:
                    print(f"[Cotton ML] Candidate Physiological Ridge loading warning: {phys_load_ex}")
                    self.phys_ridge_is_loaded = False
            else:
                self.phys_ridge_is_loaded = False

            # ---------------------------------------------
            # Load Six-District Physiological Ridge Candidate model (alpha=100, excludes Yavatmal)
            # ---------------------------------------------
            if os.path.exists(SIX_DISTRICT_MODEL_PATH):
                try:
                    self.six_dist_pipeline = joblib.load(SIX_DISTRICT_MODEL_PATH)
                    if os.path.exists(SIX_DISTRICT_METADATA_PATH):
                        with open(SIX_DISTRICT_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.six_dist_metadata = json.load(f)
                    self.six_dist_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Six-District Physiological Ridge loaded successfully: "
                        f"{self.six_dist_metadata.get('model_name', 'Ridge_Delta_Rolling_SixDistricts_Physiological')}"
                    )
                except Exception as six_load_ex:
                    print(f"[Cotton ML] Candidate Six-District Ridge loading warning: {six_load_ex}")
                    self.six_dist_is_loaded = False
            else:
                self.six_dist_is_loaded = False

            # ---------------------------------------------
            # Load Six-District Thermal-Only Ridge Candidate model (alpha=100, excludes Yavatmal)
            # ---------------------------------------------
            if os.path.exists(SIX_DISTRICT_THERMAL_MODEL_PATH):
                try:
                    self.six_dist_thermal_pipeline = joblib.load(SIX_DISTRICT_THERMAL_MODEL_PATH)
                    if os.path.exists(SIX_DISTRICT_THERMAL_METADATA_PATH):
                        with open(SIX_DISTRICT_THERMAL_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.six_dist_thermal_metadata = json.load(f)
                    self.six_dist_thermal_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Six-District Thermal Ridge loaded successfully: "
                        f"{self.six_dist_thermal_metadata.get('model_name', 'Ridge_Delta_Rolling_SixDistricts_Thermal')}"
                    )
                except Exception as six_therm_load_ex:
                    print(f"[Cotton ML] Candidate Six-District Thermal Ridge loading warning: {six_therm_load_ex}")
                    self.six_dist_thermal_is_loaded = False
            else:
                self.six_dist_thermal_is_loaded = False

            # ---------------------------------------------
            # Load Six-District Decoupled Agronomic Ridge Candidate model (alpha=100, excludes Yavatmal)
            # ---------------------------------------------
            if os.path.exists(DECOUPLED_AGRONOMIC_MODEL_PATH):
                try:
                    self.decoupled_agronomic_pipeline = joblib.load(DECOUPLED_AGRONOMIC_MODEL_PATH)
                    if os.path.exists(DECOUPLED_AGRONOMIC_METADATA_PATH):
                        with open(DECOUPLED_AGRONOMIC_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.decoupled_agronomic_metadata = json.load(f)
                    self.decoupled_agronomic_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Six-District Decoupled Agronomic Ridge loaded successfully: "
                        f"{self.decoupled_agronomic_metadata.get('model_name', 'Ridge_Delta_Rolling_SixDistricts_Decoupled_Agronomic')}"
                    )
                except Exception as dec_load_ex:
                    print(f"[Cotton ML] Candidate Six-District Decoupled Agronomic loading warning: {dec_load_ex}")
                    self.decoupled_agronomic_is_loaded = False
            else:
                self.decoupled_agronomic_is_loaded = False

            if os.path.exists(DECOUPLED_DEFICIT_HEAT_MODEL_PATH):
                try:
                    self.decoupled_deficit_heat_pipeline = joblib.load(DECOUPLED_DEFICIT_HEAT_MODEL_PATH)
                    if os.path.exists(DECOUPLED_DEFICIT_HEAT_METADATA_PATH):
                        with open(DECOUPLED_DEFICIT_HEAT_METADATA_PATH, "r", encoding="utf-8") as f:
                            self.decoupled_deficit_heat_metadata = json.load(f)
                    self.decoupled_deficit_heat_is_loaded = True
                    print(
                        f"[Cotton ML] Candidate Six-District Decoupled Deficit Heat Thresh Ridge loaded successfully: "
                        f"{self.decoupled_deficit_heat_metadata.get('model_name', 'Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh')}"
                    )
                except Exception as dec_load_ex:
                    print(f"[Cotton ML] Candidate Six-District Decoupled Deficit Heat Thresh loading warning: {dec_load_ex}")
                    self.decoupled_deficit_heat_is_loaded = False
            else:
                self.decoupled_deficit_heat_is_loaded = False


        except Exception as e:

            print(
                f"[Cotton ML] ERROR loading model: {e}"
            )

            self.is_loaded = False


    # =====================================================
    # TRANSFORMED FEATURE NAMES
    # =====================================================

    def _get_transformed_feature_names(self):

        if self.preprocessor is None:

            return []

        try:

            num_cols = (
                self.preprocessor
                .transformers_[0][2]
            )

            cat_cols = (
                self.preprocessor
                .transformers_[1][2]
            )

            ohe = (
                self.preprocessor
                .named_transformers_["cat"]
                .named_steps["onehot"]
            )

            ohe_names = list(
                ohe.get_feature_names_out(
                    cat_cols
                )
            )

            return list(num_cols) + ohe_names

        except Exception as ex:

            print(
                f"[Cotton ML] Feature-name warning: {ex}"
            )

            return []


    # =====================================================
    # DISTRICT HISTORY
    # =====================================================

    def _get_district_history(
        self,
        district: str
    ) -> dict:

        if (
            self.historical_df is None
            or district not in VALID_DISTRICTS
        ):

            return {}

        ddf = self.historical_df[
            self.historical_df["district"] == district
        ]

        if ddf.empty:

            return {}

        target = ddf[
            "yield_target_kg_ha"
        ]

        recent = (
            ddf
            .sort_values("year")
            .tail(5)
        )

        return {

            "district": district,

            "years_available":
                int(len(ddf)),

            "year_range":
                f"{int(ddf['year'].min())}–"
                f"{int(ddf['year'].max())}",

            "historical_mean_kg_ha":
                round(
                    float(target.mean()),
                    1
                ),

            "historical_min_kg_ha":
                round(
                    float(target.min()),
                    1
                ),

            "historical_max_kg_ha":
                round(
                    float(target.max()),
                    1
                ),

            "recent_5yr_mean_kg_ha":
                round(
                    float(
                        recent[
                            "yield_target_kg_ha"
                        ].mean()
                    ),
                    1
                ),

            "recent_5yr": [

                {
                    "year": int(row["year"]),

                    "yield_kg_ha":
                        round(
                            float(
                                row[
                                    "yield_target_kg_ha"
                                ]
                            ),
                            1
                        )
                }

                for _, row
                in recent.iterrows()
            ]
        }


    # =====================================================
    # LOCAL SHAP EXPLANATION
    # =====================================================

    def _generate_local_explanation(
        self,
        X_df,
        predicted_yield: float = None,
        pipeline=None,
        explainer=None,
        anchor_value: float = None,
    ) -> dict:
        """
        Generate local SHAP explanations using the Explainable AI (XAI) engine.
        Ensures additivity, waterfall steps, and non-causal agronomic summaries.
        """
        pipe = pipeline if pipeline is not None else self.pipeline
        exp = explainer if explainer is not None else (self.explainer if pipe is self.pipeline else None)

        if predicted_yield is None and pipe is not None:
            try:
                if isinstance(pipe, dict) and "model_ridge" in pipe:
                    w = pipe.get("weights", [0.55, 0.45])
                    pr = float(pipe["model_ridge"].predict(X_df)[0])
                    pt = float(pipe["model_et"].predict(X_df)[0])
                    predicted_yield = float(w[0] * pr + w[1] * pt)
                else:
                    predicted_yield = float(pipe.predict(X_df)[0])
                    if anchor_value is not None:
                        predicted_yield += float(anchor_value)
            except Exception:
                predicted_yield = 0.0

        return xai_engine.generate_local_explanation(
            pipeline=pipe,
            X_df=X_df,
            predicted_yield=predicted_yield if predicted_yield is not None else 0.0,
            explainer=exp,
            anchor_value=anchor_value,
        )


    # =====================================================
    # PREDICTION
    # =====================================================

    def predict(
        self,
        input_data: dict,
        model_version: str = None,
    ) -> dict:

        # -------------------------------------------------
        # Model loaded check
        # -------------------------------------------------

        if not self.is_loaded:

            return {

                "status": "error",

                "message":
                    "Validated cotton yield model "
                    "not loaded.",

                "is_model_loaded":
                    False
            }

        # -------------------------------------------------
        # Controlled Model Selection Mechanism
        # -------------------------------------------------
        if model_version is None:
            model_version = (
                input_data.get("model_version")
                or input_data.get("model_selection")
                or os.environ.get("AGRIPREDICT_MODEL_VERSION", "production")
            )

        norm_version = str(model_version).lower().strip()
        satellite_features_used = False
        is_delta_model = False
        is_reg_ensemble = False

        if norm_version in ["candidate_delta_rolling", "delta_rolling", "candidate_ridge_delta", "delta"]:
            if not self.delta_is_loaded:
                return {
                    "status": "error",
                    "message": "Delta rolling candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.delta_pipeline
            active_explainer = None
            active_metadata = self.delta_metadata
            active_version = "candidate_delta_rolling"
            active_model_name = self.delta_metadata.get("model_name", "Ridge_Delta_Rolling_Agronomic")
            expected_feature_cols = DELTA_ROLLING_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in ["candidate_regularized_ensemble", "regularized_ensemble", "ensemble_ridge_et", "hybrid_ensemble"]:
            if not self.reg_ensemble_is_loaded:
                return {
                    "status": "error",
                    "message": "Regularized ensemble candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.reg_ensemble_dict
            active_explainer = None
            active_metadata = self.reg_ensemble_metadata
            active_version = "candidate_regularized_ensemble"
            active_model_name = self.reg_ensemble_metadata.get("model_name", "Ensemble_Ridge_ExtraTrees_SMAP")
            expected_feature_cols = REGULARIZED_ENSEMBLE_FEATURE_COLS
            satellite_features_used = True
            is_reg_ensemble = True

        elif norm_version in [
            "candidate_repaired_synth",
            "repaired_synth",
            "candidate_repaired",
            "repaired",
            "repaired_biophysical_synth",
        ]:
            if not getattr(self, "repaired_synth_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Repaired synthetic candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.repaired_synth_pipeline
            active_explainer = None
            active_metadata = self.repaired_synth_metadata
            active_version = "candidate_repaired_synth"
            active_model_name = self.repaired_synth_metadata.get("model_name", "Ridge_Delta_Repaired_Synth_sw010")
            expected_feature_cols = DELTA_ROLLING_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in [
            "candidate_physiological_ridge_a100",
            "physiological_ridge_a100",
            "candidate_physiological_ridge",
            "physiological_ridge",
            "phys_ridge_a100",
            "phys_ridge",
        ]:
            if not getattr(self, "phys_ridge_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Physiological Ridge candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.phys_ridge_pipeline
            active_explainer = None
            active_metadata = self.phys_ridge_metadata
            active_version = "candidate_physiological_ridge_a100"
            active_model_name = self.phys_ridge_metadata.get("model_name", "Ridge_Delta_Rolling_Physiological_a100")
            expected_feature_cols = PHYSIOLOGICAL_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in [
            "candidate_six_district_thermal",
            "six_district_thermal",
            "six_district_thermal_ridge",
            "candidate_thermal_ridge",
            "thermal_ridge",
            "six_dist_thermal",
        ]:
            if not getattr(self, "six_dist_thermal_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Six-district thermal candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            req_dist = str(input_data.get("district", "")).strip().capitalize()
            if req_dist == "Yavatmal":
                return {
                    "status": "error",
                    "message": (
                        "The candidate model 'candidate_six_district_thermal' excludes Yavatmal district by design. "
                        "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                    ),
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": True,
                    "model_version": "candidate_six_district_thermal",
                }
            active_pipeline = self.six_dist_thermal_pipeline
            active_explainer = None
            active_metadata = self.six_dist_thermal_metadata
            active_version = "candidate_six_district_thermal"
            active_model_name = self.six_dist_thermal_metadata.get(
                "model_name", "Ridge_Delta_Rolling_SixDistricts_Thermal"
            )
            expected_feature_cols = THERMAL_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in [
            "candidate_six_district_decoupled_agronomic",
            "six_district_decoupled_agronomic",
            "candidate_decoupled_agronomic",
            "decoupled_agronomic",
            "decoupled_ridge",
        ]:
            if not getattr(self, "decoupled_agronomic_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Six-district decoupled agronomic candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            req_dist = str(input_data.get("district", "")).strip().capitalize()
            if req_dist == "Yavatmal":
                return {
                    "status": "error",
                    "message": (
                        "The candidate model 'candidate_six_district_decoupled_agronomic' excludes Yavatmal district by design. "
                        "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                    ),
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": True,
                    "model_version": "candidate_six_district_decoupled_agronomic",
                }
            active_pipeline = self.decoupled_agronomic_pipeline
            active_explainer = None
            active_metadata = self.decoupled_agronomic_metadata
            active_version = "candidate_six_district_decoupled_agronomic"
            active_model_name = self.decoupled_agronomic_metadata.get(
                "model_name", "Ridge_Delta_Rolling_SixDistricts_Decoupled_Agronomic"
            )
            expected_feature_cols = DECOUPLED_AGRONOMIC_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in [
            "candidate_six_district_dar_deficit_heat_thresh",
            "six_district_dar_deficit_heat_thresh",
            "candidate_dar_deficit_heat_thresh",
            "dar_deficit_heat_thresh",
            "candidate_six_district_decoupled_deficit_heatthresh_a75",
            "decoupled_deficit_heatthresh",
        ]:
            if not getattr(self, "decoupled_deficit_heat_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Six-district decoupled deficit heat thresh candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            req_dist = str(input_data.get("district", "")).strip().capitalize()
            if req_dist == "Yavatmal":
                return {
                    "status": "error",
                    "message": (
                        "The candidate model 'candidate_six_district_dar_deficit_heat_thresh' excludes Yavatmal district by design. "
                        "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                    ),
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": True,
                    "model_version": "candidate_six_district_dar_deficit_heat_thresh",
                }
            active_pipeline = self.decoupled_deficit_heat_pipeline
            active_explainer = None
            active_metadata = self.decoupled_deficit_heat_metadata
            active_version = "candidate_six_district_dar_deficit_heat_thresh"
            active_model_name = self.decoupled_deficit_heat_metadata.get(
                "model_name", "Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh"
            )
            expected_feature_cols = DECOUPLED_DEFICIT_HEAT_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in [
            "candidate_six_district_physiological",
            "six_district_physiological",
            "six_district_ridge",
            "candidate_six_district",
            "six_district",
            "six_dist_physiological",
        ]:
            if not getattr(self, "six_dist_is_loaded", False):
                return {
                    "status": "error",
                    "message": "Six-district physiological candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            req_dist = str(input_data.get("district", "")).strip().capitalize()
            if req_dist == "Yavatmal":
                return {
                    "status": "error",
                    "message": (
                        "The candidate model 'candidate_six_district_physiological' excludes Yavatmal district by design. "
                        "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                    ),
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": True,
                    "model_version": "candidate_six_district_physiological",
                }
            active_pipeline = self.six_dist_pipeline
            active_explainer = None
            active_metadata = self.six_dist_metadata
            active_version = "candidate_six_district_physiological"
            active_model_name = self.six_dist_metadata.get(
                "model_name", "Ridge_Delta_Rolling_SixDistricts_Physiological"
            )
            expected_feature_cols = PHYSIOLOGICAL_FEATURE_COLS
            satellite_features_used = False
            is_delta_model = True

        elif norm_version in ["candidate_satellite_smap", "satellite_smap", "smap", "candidate_satellite"]:
            if not self.satellite_is_loaded:
                return {
                    "status": "error",
                    "message": "Satellite candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.satellite_pipeline
            active_explainer = self.satellite_explainer
            active_metadata = self.satellite_metadata
            active_version = "candidate_satellite_smap"
            active_model_name = self.satellite_metadata.get("model_name", "GradientBoosting_Satellite_SMAP")
            expected_feature_cols = SATELLITE_FEATURE_COLS
            satellite_features_used = True
        elif norm_version in ["optimized", "optimized_sw005", "candidate_optimized", "opt", "optimized_leakage_safe_sw005"]:
            if not self.opt_is_loaded:
                return {
                    "status": "error",
                    "message": "Optimized candidate model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.opt_pipeline
            active_explainer = self.opt_explainer
            active_metadata = self.opt_metadata
            active_version = "candidate_optimized"
            active_model_name = self.opt_metadata.get("model_name", "GradientBoosting_Optimized_sw005")
            expected_feature_cols = FEATURE_COLS
        elif norm_version in ["candidate", "candidate_synthetic", "synth_100pct", "synthetic_augmented"]:
            if not self.candidate_is_loaded:
                return {
                    "status": "error",
                    "message": "Candidate synthetic model is not currently available or failed to load.",
                    "is_model_loaded": self.is_loaded,
                    "candidate_available": False,
                }
            active_pipeline = self.candidate_pipeline
            active_explainer = self.candidate_explainer
            active_metadata = self.candidate_metadata
            active_version = "candidate_synthetic"
            active_model_name = self.candidate_metadata.get("model_name", "GradientBoosting_Synth_100pct")
            expected_feature_cols = FEATURE_COLS
        elif norm_version in ["production", "default", ""]:
            active_pipeline = self.pipeline
            active_explainer = self.explainer
            active_metadata = self.metadata
            active_version = "production"
            active_model_name = self.metadata.get("model_name", "GradientBoosting")
            expected_feature_cols = FEATURE_COLS
        else:
            return {
                "status": "error",
                "message": (
                    f"Unknown model_version '{model_version}'. "
                    "Valid options: ['production', 'candidate_repaired_synth', 'candidate_delta_rolling', 'candidate_regularized_ensemble', 'candidate_satellite_smap', 'candidate_optimized', 'candidate_synthetic']"
                ),
                "valid_versions": [
                    "production",
                    "candidate_repaired_synth",
                    "candidate_delta_rolling",
                    "candidate_regularized_ensemble",
                    "candidate_satellite_smap",
                    "candidate_optimized",
                    "candidate_synthetic"
                ]
            }


        # -------------------------------------------------
        # District validation
        # -------------------------------------------------

        district = input_data.get(
            "district",
            ""
        )

        if district not in VALID_DISTRICTS:

            return {

                "status": "error",

                "message":
                    f"District '{district}' is not "
                    "a valid Vidarbha district.",

                "valid_districts":
                    VALID_DISTRICTS
            }


        # -------------------------------------------------
        # Feature validation: reject target leakage or invalid schema
        # -------------------------------------------------

        TARGET_COL = "yield_target_kg_ha"
        if TARGET_COL in input_data:
            return {
                "status": "error",
                "message": (
                    f"Target column '{TARGET_COL}' must not be passed into model features. "
                    "Feature inputs must be strictly non-target explanatory variables."
                ),
            }

        # Check for unknown feature keys
        allowed_meta_keys = {"year", "target_year", "model_selection", "model_version", "rolling_3yr_yield_mean_kg_ha"}
        unknown_keys = [
            k for k in input_data.keys()
            if k not in expected_feature_cols and k not in allowed_meta_keys
        ]
        if unknown_keys:
            return {
                "status": "error",
                "message": f"Unknown or disallowed feature columns provided: {unknown_keys}",
                "allowed_features": expected_feature_cols,
            }

        # Check required satellite features if satellite/ensemble candidate requested
        if satellite_features_used:
            smap_cols_to_check = ENSEMBLE_SMAP_FEATURES if is_reg_ensemble else SATELLITE_SMAP_FEATURES
            missing_smap = [
                k for k in smap_cols_to_check
                if k not in input_data or input_data[k] is None or (
                    isinstance(input_data[k], (float, np.floating)) and np.isnan(input_data[k])
                )
            ]
            if missing_smap:
                return {
                    "status": "error",
                    "message": (
                        f"Missing required NASA SMAP soil moisture features: {missing_smap}. "
                        "Satellite/ensemble candidate model requires verified satellite observations and does not permit synthetic or fabricated fallback."
                    ),
                    "missing_satellite_features": missing_smap,
                }

        # Check that we have at least essential meteorological or historical features
        provided_features = [
            k for k in expected_feature_cols
            if k in input_data and input_data[k] is not None and not (
                isinstance(input_data[k], (float, np.floating)) and np.isnan(input_data[k])
            )
        ]
        if len(provided_features) < 5:
            return {
                "status": "error",
                "message": (
                    f"Insufficient features provided. Only {len(provided_features)} valid features were provided. "
                    "Expected valid feature values for authoritative model features."
                ),
                "provided_count": len(provided_features),
            }

        # -------------------------------------------------
        # Build model feature row
        # -------------------------------------------------

        row = {}

        missing_lag_features = []

        for col in expected_feature_cols:

            val = input_data.get(
                col
            )

            # Treat missing values as NaN.

            if (
                val is None
                or (
                    isinstance(
                        val,
                        (float, np.floating)
                    )
                    and np.isnan(val)
                )
            ):

                row[col] = np.nan

                if (
                    col
                    in FEATURE_AVAILABILITY.get(
                        "lag_features_require_prior_year_data", []
                    )
                ):

                    missing_lag_features.append(
                        col
                    )

            else:

                row[col] = val

        # Ensure exact feature ordering.

        X = pd.DataFrame(
            [row],
            columns=expected_feature_cols
        )


        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------
        # Prediction & Local SHAP
        # -------------------------------------------------

        try:
            if is_delta_model:
                anchor = input_data.get("rolling_3yr_yield_mean_kg_ha")
                if anchor is None or (
                    isinstance(anchor, (float, np.floating)) and np.isnan(anchor)
                ):
                    return {
                        "status": "error",
                        "message": (
                            "Missing required 3-year rolling average yield (rolling_3yr_yield_mean_kg_ha) "
                            "for historical anchor calculation. This model formulation requires prior historical yields."
                        ),
                        "is_model_loaded": self.is_loaded,
                        "model_version": active_version,
                    }
                anchor = float(anchor)
                raw_delta = float(active_pipeline.predict(X)[0])
                predicted_yield = max(0.0, float(anchor + raw_delta))
                local_xai = self._generate_local_explanation(
                    X,
                    predicted_yield,
                    pipeline=active_pipeline,
                    anchor_value=anchor,
                )
            elif is_reg_ensemble:
                p_ridge = float(active_pipeline["model_ridge"].predict(X)[0])
                p_et = float(active_pipeline["model_et"].predict(X)[0])
                weights = active_pipeline.get("weights", [0.55, 0.45])
                predicted_yield = max(0.0, float(weights[0] * p_ridge + weights[1] * p_et))
                local_xai = self._generate_local_explanation(
                    X,
                    predicted_yield,
                    pipeline=active_pipeline,
                )
            else:
                predicted_yield = float(active_pipeline.predict(X)[0])
                predicted_yield = max(0.0, predicted_yield)
                local_xai = self._generate_local_explanation(
                    X,
                    predicted_yield,
                    pipeline=active_pipeline,
                    explainer=active_explainer,
                )

        except Exception as ex:

            return {

                "status": "error",

                "message":
                    f"Prediction failed: {str(ex)}",

                "is_model_loaded":
                    self.is_loaded,

                "model_version":
                    active_version,
            }


        # -------------------------------------------------
        # Validation metadata (sourced from active model)
        # -------------------------------------------------

        validation_2011_2023 = (
            active_metadata.get(
                "validation_metrics_2011_2023",
                {}
            )
        )

        holdout_2024 = (
            active_metadata.get(
                "holdout_2024_metrics",
                {}
            )
        )


        val_mae = (
            validation_2011_2023
            .get("Mean_MAE")
        )

        val_mae_std = (
            validation_2011_2023
            .get("Std_MAE")
        )


        # -------------------------------------------------
        # District historical context
        # -------------------------------------------------

        district_history = (
            self._get_district_history(
                district
            )
        )

        hist_mean = (
            district_history.get(
                "historical_mean_kg_ha"
            )
        )


        # -------------------------------------------------
        # Warnings
        # -------------------------------------------------

        warnings = []


        if missing_lag_features:

            warnings.append(
                "Missing lag features "
                f"({', '.join(missing_lag_features)}) "
                "were imputed using the model's "
                "training-time preprocessing. "
                "Providing prior-year recorded yield "
                "values is recommended."
            )


        # -------------------------------------------------
        # Global feature importance
        # -------------------------------------------------

        global_fi_formatted = []


        for item in self.feature_importance:

            f_raw = item.get(
                "feature",
                ""
            )

            display_name = (
                HUMAN_READABLE_NAMES.get(
                    f_raw,
                    f_raw
                    .replace("_", " ")
                    .title()
                )
            )


            global_fi_formatted.append({

                "feature":
                    f_raw,

                "display_name":
                    display_name,

                "importance":
                    item.get(
                        "importance",
                        0
                    )
            })


        # -------------------------------------------------
        # Conformal Prediction Uncertainty Calibration
        #
        # Calibrated on 13-fold chronological out-of-fold residuals (2011-2023, N=78)
        # Empirical coverage: 80% -> 82.1%, 90% -> 92.3% (100% on 2024 holdout), 95% -> 97.4%
        # -------------------------------------------------
        coverage_warnings = []
        if float(predicted_yield) > 500.0:
            coverage_warnings.append(
                "High-yield regime warning: In bumper seasons (>500 kg/ha), empirical historical coverage of these bounds drops to 71.4% due to model shrinkage toward the rolling historical anchor."
            )
        if district and str(district).strip().lower() == "amravati":
            coverage_warnings.append(
                "District variance warning: Amravati has exhibited higher historical yield variance across 2011–2023, resulting in empirical coverage of 76.9% at the nominal 90% level."
            )

        for cw in coverage_warnings:
            if cw not in warnings:
                warnings.append(cw)

        prediction_interval_data = {
            "label": "Empirically Calibrated Out-of-Fold Error Bounds",
            "description": "Empirically Calibrated Out-of-Fold Error Bounds",
            "disclaimer": "These are empirical historical error bounds from 2011–2023 out-of-fold cross-validation residuals (retrospectively pooled), NOT guaranteed theoretical Gaussian confidence intervals. Strict rolling-origin prospective coverage is 87.9% across eligible years 2013–2023, and may degrade to 16.7% during bumper post-drought surges.",
            "is_guaranteed_confidence_interval": False,
            "confidence_level": "90%",
            "lower_bound_kg_per_ha": max(0.0, round(float(predicted_yield) - 253.5, 1)),
            "upper_bound_kg_per_ha": round(float(predicted_yield) + 253.5, 1),
            "lower_bound_kg_ha": max(0.0, round(float(predicted_yield) - 253.5, 1)),
            "upper_bound_kg_ha": round(float(predicted_yield) + 253.5, 1),
            "half_width_kg_ha": 253.5,
            "interval_range_kg_per_ha": round(min(float(predicted_yield), 253.5) + 253.5, 1),
            "calibration_method": "Empirically Calibrated Out-of-Fold Error Bounds (Retrospective 2011–2023)",
            "calibration_source": "13-fold chronological out-of-fold residuals (2011-2023, N=78)",
            "conformal_half_width_kg_ha": 253.5,
            "empirical_half_width_kg_ha": 253.5,
            "empirical_cv_coverage": "92.3%",
            "empirical_holdout_coverage": "100.0%",
            "coverage_warnings": coverage_warnings,
            "limitations": [
                "Empirical historical bounds: derived from 2011–2023 out-of-fold historical residuals; not a distribution-free theoretical guarantee.",
                "Retrospective circularity: The 92.3% retrospective OOF coverage is circular because the same 78 residuals determined and evaluated the ±253.5 kg/ha threshold.",
                "Strict prospective rolling-origin coverage is 87.9% across eligible years (2013–2023, N=66); during the 2016 bumper post-drought recovery, coverage dropped to 16.7%.",
                "The 2024 holdout covered 6/6 observations, but this sample is too small to establish long-term coverage guarantees.",
                "High-yield regime under-coverage: In bumper seasons (>500 kg/ha), empirical historical coverage drops to 71.4% due to L2 shrinkage toward the rolling historical anchor.",
                "Amravati variance under-coverage: Amravati has exhibited higher historical yield variance across 2011–2023, resulting in empirical coverage of 76.9% at the nominal 90% level.",
                "Unmodeled shocks: Sudden late-season pest outbreaks (e.g. pink bollworm) or unseasonal post-monsoon cyclonic showers not captured in Kharif weather indices may fall outside these bounds."
            ],
            "all_confidence_levels": {
                "80%": {
                    "lower_bound_kg_per_ha": max(0.0, round(float(predicted_yield) - 177.0, 1)),
                    "upper_bound_kg_per_ha": round(float(predicted_yield) + 177.0, 1),
                    "half_width_kg_ha": 177.0,
                    "empirical_cv_coverage": "82.1%",
                },
                "90%": {
                    "lower_bound_kg_per_ha": max(0.0, round(float(predicted_yield) - 253.5, 1)),
                    "upper_bound_kg_per_ha": round(float(predicted_yield) + 253.5, 1),
                    "half_width_kg_ha": 253.5,
                    "empirical_cv_coverage": "92.3%",
                },
                "95%": {
                    "lower_bound_kg_per_ha": max(0.0, round(float(predicted_yield) - 293.8, 1)),
                    "upper_bound_kg_per_ha": round(float(predicted_yield) + 293.8, 1),
                    "half_width_kg_ha": 293.8,
                    "empirical_cv_coverage": "97.4%",
                },
            },
        }

        # -------------------------------------------------
        # Final API response
        # -------------------------------------------------

        return {

            "status":
                "success",

            "is_real_model":
                True,

            "model_version":
                active_version,

            "model_name":
                active_model_name,

            "crop":
                "Cotton (Gossypium hirsutum)",

            "district":
                district,

            "predicted_yield_kg_ha":
                round(
                    predicted_yield,
                    1
                ),

            "predicted_yield_quintal_ha":
                round(float(predicted_yield) / 100.0, 2),

            "predicted_yield_quintal_acre":
                round(float(predicted_yield) / 100.0 * 0.404686, 2),

            "unit":
                "kg/ha",

            "satellite_features_used":
                satellite_features_used,

            "model_selection_info": {
                "active_version": active_version,
                "model_name": active_model_name,
                "satellite_features_used": satellite_features_used,
                "candidate_available": self.candidate_is_loaded,
                "optimized_candidate_available": self.opt_is_loaded,
                "satellite_candidate_available": self.satellite_is_loaded,
                "delta_rolling_candidate_available": self.delta_is_loaded,
                "regularized_ensemble_candidate_available": self.reg_ensemble_is_loaded,
                "repaired_synth_candidate_available": getattr(self, "repaired_synth_is_loaded", False),
                "production_sha256": "3b0c2fda194cd923e4957b4637f3a97e5df3fd885623c9eb182588dca816bd8e",
            },

            "prediction_interval": prediction_interval_data,


            # -------------------------------------------------
            # Transparent validation context
            #
            # IMPORTANT:
            # This is NOT a confidence interval.
            # -------------------------------------------------

            "validation_context": {

                "training_period":
                    str(active_metadata.get(
                        "training_years",
                        active_metadata.get("dataset_provenance", {}).get("training_rows_through_2023", "1997-2023")
                    )),

                "validation_period":
                    "2011–2023",

                "temporal_folds":
                    13,

                "mean_mae_kg_ha":
                    (
                        round(
                            float(val_mae),
                            1
                        )
                        if val_mae is not None
                        else None
                    ),

                "std_mae_kg_ha":
                    (
                        round(
                            float(val_mae_std),
                            1
                        )
                        if val_mae_std is not None
                        else None
                    ),

                "final_holdout_year":
                    active_metadata.get(
                        "holdout_year",
                        2024
                    ),

                "holdout_mae_kg_ha":
                    (
                        round(
                            float(
                                holdout_2024.get(
                                    "MAE"
                                )
                            ),
                            1
                        )
                        if holdout_2024.get(
                            "MAE"
                        ) is not None
                        else None
                    ),

                "holdout_rmse_kg_ha":
                    (
                        round(
                            float(
                                holdout_2024.get(
                                    "RMSE"
                                )
                            ),
                            1
                        )
                        if holdout_2024.get(
                            "RMSE"
                        ) is not None
                        else None
                    ),

                "holdout_r2":
                    (
                        round(
                            float(
                                holdout_2024.get(
                                    "R2"
                                )
                            ),
                            3
                        )
                        if holdout_2024.get(
                            "R2"
                        ) is not None
                        else None
                    ),

                "holdout_mape_percent":
                    (
                        round(
                            float(
                                holdout_2024.get(
                                    "MAPE"
                                )
                            ),
                            2
                        )
                        if holdout_2024.get(
                            "MAPE"
                        ) is not None
                        else None
                    )
            },


            # -------------------------------------------------
            # District historical context
            # -------------------------------------------------

            "district_historical_context":
                district_history,


            "vs_district_historical_mean":
                (
                    round(
                        predicted_yield - hist_mean,
                        1
                    )
                    if hist_mean is not None
                    else None
                ),


            # -------------------------------------------------
            # SHAP / XAI
            # -------------------------------------------------

            "explanation":
                local_xai,


            # -------------------------------------------------
            # Validation metrics
            #
            # Kept as a compact compatibility block.
            # All values come from the new metadata.
            # -------------------------------------------------

            "validation_metrics": {

                "Mean_MAE_kg_ha":
                    (
                        round(
                            float(val_mae),
                            1
                        )
                        if val_mae is not None
                        else None
                    ),

                "Std_MAE_kg_ha":
                    (
                        round(
                            float(val_mae_std),
                            1
                        )
                        if val_mae_std is not None
                        else None
                    ),

                "Mean_RMSE_kg_ha":
                    (
                        round(
                            float(
                                validation_2011_2023.get(
                                    "Mean_RMSE"
                                )
                            ),
                            1
                        )
                        if validation_2011_2023.get(
                            "Mean_RMSE"
                        ) is not None
                        else None
                    ),

                "Mean_R2":
                    (
                        round(
                            float(
                                validation_2011_2023.get(
                                    "Mean_R2"
                                )
                            ),
                            3
                        )
                        if validation_2011_2023.get(
                            "Mean_R2"
                        ) is not None
                        else None
                    ),

                "Mean_MAPE_percent":
                    (
                        round(
                            float(
                                validation_2011_2023.get(
                                    "Mean_MAPE"
                                )
                            ),
                            2
                        )
                        if validation_2011_2023.get(
                            "Mean_MAPE"
                        ) is not None
                        else None
                    ),

                "temporal_folds":
                    "2011–2023 (13-fold expanding window)"
            },


            # -------------------------------------------------
            # Global feature importance
            # -------------------------------------------------

            "global_top_features":
                global_fi_formatted[:10],

            "global_shap_importance":
                xai_engine.get_global_importance(),


            # -------------------------------------------------
            # Warnings
            # -------------------------------------------------

            "warnings":
                warnings
        }


# =========================================================
# SINGLETON
# =========================================================

cotton_predictor = CottonYieldPredictor()