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

# Legacy/global feature importance file.
# This is kept for compatibility with the existing project.
FI_PATH = os.path.join(
    _ARTIFACTS,
    "feature_importance.json"
)

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(_ML_ROOT)),
    "data",
    "vidarbha_cotton_model_ready_1997_2024.csv"
)


# =========================================================
# VALID DISTRICTS
# =========================================================

VALID_DISTRICTS = [
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim",
    "Yavatmal"
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


# =========================================================
# HUMAN-READABLE FEATURE NAMES
# =========================================================

HUMAN_READABLE_NAMES = {

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
        X_df
    ) -> dict:

        if (
            self.explainer is None
            or self.preprocessor is None
        ):

            return {
                "available": False
            }

        try:

            # Transform input using the exact
            # production preprocessor.

            X_trans = (
                self.preprocessor
                .transform(X_df)
            )


            # SHAP values for one sample

            shap_output = (
                self.explainer
                .shap_values(X_trans)
            )

            shap_vals = shap_output[0]


            # Expected/base model value

            base_val = (
                self.explainer
                .expected_value
            )

            if isinstance(
                base_val,
                np.ndarray
            ):

                base_val = float(
                    base_val[0]
                )


            feature_names = (
                self._get_transformed_feature_names()
            )


            contributions = []

            for feat_raw, val in zip(
                feature_names,
                shap_vals
            ):

                display_name = (
                    HUMAN_READABLE_NAMES.get(
                        feat_raw,
                        feat_raw
                        .replace("_", " ")
                        .title()
                    )
                )

                val_round = round(
                    float(val),
                    2
                )

                # Ignore extremely small numerical noise.

                if abs(val_round) >= 0.05:

                    contributions.append({

                        "feature":
                            feat_raw,

                        "display_name":
                            display_name,

                        "contribution_kg_ha":
                            val_round,

                        "direction":
                            (
                                "positive"
                                if val_round > 0
                                else "negative"
                            )
                    })


            # Largest absolute effects first

            contributions.sort(
                key=lambda x:
                    abs(
                        x[
                            "contribution_kg_ha"
                        ]
                    ),
                reverse=True
            )


            pos_factors = [
                c
                for c in contributions
                if c["direction"] == "positive"
            ][:5]


            neg_factors = [
                c
                for c in contributions
                if c["direction"] == "negative"
            ][:5]


            top_chart_features = (
                contributions[:10]
            )


            # Natural-language summary

            top_pos_names = [
                f["display_name"]
                for f in pos_factors[:2]
            ]

            top_neg_names = [
                f["display_name"]
                for f in neg_factors[:2]
            ]


            summary_parts = []


            if top_pos_names:

                summary_parts.append(
                    "Higher estimated yield was "
                    "supported by "
                    + ", ".join(
                        top_pos_names
                    )
                    + "."
                )


            if top_neg_names:

                summary_parts.append(
                    "The estimate was offset by "
                    + ", ".join(
                        top_neg_names
                    )
                    + "."
                )


            if not summary_parts:

                summary_parts.append(
                    "The yield estimate reflects "
                    "balanced historical and climatic "
                    "indicators."
                )


            summary_text = " ".join(
                summary_parts
            )


            return {

                "available": True,

                "methodology":
                    "SHAP (SHapley Additive "
                    "exPlanations) TreeExplainer",

                "base_value_kg_ha":
                    round(
                        float(base_val),
                        1
                    ),

                "summary_text":
                    summary_text,

                "increasing_factors":
                    pos_factors,

                "decreasing_factors":
                    neg_factors,

                "top_influential_features":
                    top_chart_features
            }


        except Exception as ex:

            print(
                f"[Cotton ML] SHAP error: {ex}"
            )

            return {

                "available": False,

                "error":
                    str(ex)
            }


    # =====================================================
    # PREDICTION
    # =====================================================

    def predict(
        self,
        input_data: dict
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
        # Build model feature row
        # -------------------------------------------------

        row = {}

        missing_lag_features = []


        for col in FEATURE_COLS:

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
                    in FEATURE_AVAILABILITY[
                        "lag_features_require_prior_year_data"
                    ]
                ):

                    missing_lag_features.append(
                        col
                    )

            else:

                row[col] = val


        # Ensure exact feature ordering.

        X = pd.DataFrame(
            [row],
            columns=FEATURE_COLS
        )


        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------

        try:

            predicted_yield = float(
                self.pipeline.predict(X)[0]
            )

            # Yield cannot logically be negative.

            predicted_yield = max(
                0.0,
                predicted_yield
            )

        except Exception as ex:

            return {

                "status": "error",

                "message":
                    f"Prediction failed: {str(ex)}",

                "is_model_loaded":
                    self.is_loaded
            }


        # -------------------------------------------------
        # Local SHAP
        # -------------------------------------------------

        local_xai = (
            self._generate_local_explanation(X)
        )


        # -------------------------------------------------
        # Validation metadata
        # -------------------------------------------------

        validation_2011_2023 = (
            self.metadata.get(
                "validation_metrics_2011_2023",
                {}
            )
        )

        holdout_2024 = (
            self.metadata.get(
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
        # Final API response
        # -------------------------------------------------

        return {

            "status":
                "success",

            "is_real_model":
                True,

            "model_name":
                self.metadata.get(
                    "model_name",
                    "GradientBoosting"
                ),

            "crop":
                "Cotton (Gossypium hirsutum)",

            "district":
                district,

            "predicted_yield_kg_ha":
                round(
                    predicted_yield,
                    1
                ),

            "unit":
                "kg/ha",


            # -------------------------------------------------
            # Transparent validation context
            #
            # IMPORTANT:
            # This is NOT a confidence interval.
            # -------------------------------------------------

            "validation_context": {

                "training_period":
                    self.metadata.get(
                        "training_years",
                        "1997-2023"
                    ),

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
                    self.metadata.get(
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