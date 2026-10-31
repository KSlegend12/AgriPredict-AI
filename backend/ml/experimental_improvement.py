"""
AgriPredict-AI
Experimental 2024/2025 Cotton Yield Improvement Study

IMPORTANT:
- Production model is NOT modified.
- Production final_model.pkl is NOT overwritten.
- 2024 remains a one-shot holdout.
- 2025 is evaluated separately as an experimental end-of-season hindcast.
- Yavatmal is retained.
- Model selection/tuning uses only 2011-2023.
"""

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT / "backend" / "data" / "vidarbha_cotton_model_ready_1997_2024.csv"

INPUT_2025_PATH = (
    ROOT / "data" / "cotton_2025_experimental_model_input.csv"
)

TARGET_2025_PATH = (
    ROOT / "data" / "cotton_2025_experimental_predictions.csv"
)

OUTPUT_DIR = (
    ROOT / "backend" / "ml" / "evaluation" / "experimental_improvement"
)

ARTIFACT_DIR = (
    ROOT / "backend" / "ml" / "artifacts" / "experimental_improvement"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "yield_target_kg_ha"
YEAR_COL = "year"
DISTRICT_COL = "district"

HOLDOUT_YEAR = 2024
SELECTION_START_YEAR = 2011

RANDOM_STATE = 42


# ============================================================
# FEATURE GROUPS
# ============================================================

LAG_FEATURES = [
    "previous_year_yield_kg_ha",
    "previous_2year_yield_kg_ha",
    "rolling_3yr_yield_mean_kg_ha",
]

AREA_FEATURES = [
    "cotton_area_000ha",
]

WEATHER_FEATURES = [
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
    "rainfall_monsoon_mm_district_anomaly",
    "rainfall_kharif_mm_district_anomaly",
    "tmax_kharif_mean_c_district_anomaly",
    "tmin_kharif_mean_c_district_anomaly",
]


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    non_zero = np.abs(y_true) > 1e-12

    if np.any(non_zero):
        mape = (
            np.mean(
                np.abs(
                    (y_true[non_zero] - y_pred[non_zero])
                    / y_true[non_zero]
                )
            )
            * 100
        )
    else:
        mape = np.nan

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
        "MAPE_percent": float(mape),
    }


# ============================================================
# FEATURE STRATEGIES
# ============================================================

def build_feature_sets(all_features):
    """
    Four controlled feature strategies.

    1. baseline:
       All 36 production features.

    2. no_lag:
       Weather + area + district.
       Removes autoregressive yield features.

    3. weather_lag:
       Weather + area + yield-lag features + district.

    4. weather_area:
       Weather + area + district.
       Kept explicitly as a separate named experiment.
    """

    baseline = list(all_features)

    no_lag = [
        c
        for c in all_features
        if c not in LAG_FEATURES
    ]

    weather_lag = [
        DISTRICT_COL
    ] + AREA_FEATURES + WEATHER_FEATURES + LAG_FEATURES

    weather_area = [
        DISTRICT_COL
    ] + AREA_FEATURES + WEATHER_FEATURES

    # Remove accidental duplicates while preserving order.
    def unique(items):
        return list(dict.fromkeys(items))

    return {
        "baseline_36_features": unique(baseline),
        "no_lag": unique(no_lag),
        "weather_lag": unique(weather_lag),
        "weather_area": unique(weather_area),
    }


# ============================================================
# PREPROCESSOR
# ============================================================

def build_pipeline(model, feature_columns):
    categorical = [
        c for c in feature_columns
        if c == DISTRICT_COL
    ]

    numerical = [
        c for c in feature_columns
        if c != DISTRICT_COL
    ]

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                numeric_pipeline,
                numerical,
            ),
            (
                "cat",
                categorical_pipeline,
                categorical,
            ),
        ],
        remainder="drop",
    )

    return Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )


# ============================================================
# MODEL CANDIDATES
# ============================================================

def get_models():
    return {
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_STATE,
        ),

        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),

        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),

        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.05,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=RANDOM_STATE,
        ),

        "Ridge": Pipeline(
            steps=[
                (
                    "scale",
                    StandardScaler(),
                ),
                (
                    "ridge",
                    Ridge(alpha=10.0),
                ),
            ]
        ),
    }


# ============================================================
# EXPANDING WINDOW VALIDATION
# ============================================================

def expanding_window_cv(
    df,
    feature_columns,
    model,
    start_year=2011,
    end_year=2023,
):
    rows = []

    years = sorted(
        y
        for y in df[YEAR_COL].unique()
        if start_year <= y <= end_year
    )

    for validation_year in years:
        train = df[
            df[YEAR_COL] < validation_year
        ].copy()

        validation = df[
            df[YEAR_COL] == validation_year
        ].copy()

        if train.empty or validation.empty:
            continue

        X_train = train[feature_columns]
        y_train = train[TARGET]

        X_val = validation[feature_columns]
        y_val = validation[TARGET]

        fitted = build_pipeline(model, feature_columns)

        fitted.fit(
            X_train,
            y_train,
        )

        pred = fitted.predict(X_val)

        metrics = calculate_metrics(
            y_val,
            pred,
        )

        rows.append(
            {
                "validation_year": validation_year,
                **metrics,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# TRAIN 1997-2023 AND TEST 2024
# ============================================================

def evaluate_2024(
    df,
    feature_columns,
    model,
):
    train = df[
        df[YEAR_COL] < HOLDOUT_YEAR
    ].copy()

    test = df[
        df[YEAR_COL] == HOLDOUT_YEAR
    ].copy()

    X_train = train[feature_columns]
    y_train = train[TARGET]

    X_test = test[feature_columns]
    y_test = test[TARGET]

    fitted = build_pipeline(model, feature_columns)

    fitted.fit(
        X_train,
        y_train,
    )

    pred = fitted.predict(X_test)

    metrics = calculate_metrics(
        y_test,
        pred,
    )

    district_results = test[
        [DISTRICT_COL, TARGET]
    ].copy()

    district_results[
        "predicted_yield_kg_ha"
    ] = pred

    district_results[
        "abs_error_kg_ha"
    ] = np.abs(
        district_results[TARGET]
        - district_results["predicted_yield_kg_ha"]
    )

    district_results[
        "pct_error"
    ] = (
        district_results["abs_error_kg_ha"]
        / district_results[TARGET].abs()
        * 100
    )

    return fitted, metrics, district_results


# ============================================================
# 2025 EXPERIMENTAL HINDCAST
# ============================================================

def load_2025_data():
    X_2025 = pd.read_csv(
        INPUT_2025_PATH
    )

    target_2025 = pd.read_csv(
        TARGET_2025_PATH
    )

    required_target_columns = {
        DISTRICT_COL,
        "third_advance_estimate_2025_26_kg_ha",
    }

    missing = (
        required_target_columns
        - set(target_2025.columns)
    )

    if missing:
        raise ValueError(
            "2025 target file missing columns: "
            + str(sorted(missing))
        )

    target_2025 = target_2025[
        [
            DISTRICT_COL,
            "third_advance_estimate_2025_26_kg_ha",
        ]
    ]

    merged = X_2025.merge(
        target_2025,
        on=DISTRICT_COL,
        how="inner",
        validate="one_to_one",
    )

    if len(merged) != 7:
        raise ValueError(
            f"Expected 7 districts for 2025, "
            f"got {len(merged)}"
        )

    return merged


def evaluate_2025(
    df,
    feature_columns,
    model,
):
    train = df[
        df[YEAR_COL] <= 2023
    ].copy()

    # IMPORTANT:
    # 2024 is intentionally not used for training here.
    # This keeps the comparison conservative.
    X_train = train[feature_columns]
    y_train = train[TARGET]

    test_2025 = load_2025_data()

    X_2025 = test_2025[
        feature_columns
    ]

    y_2025 = test_2025[
        "third_advance_estimate_2025_26_kg_ha"
    ]

    fitted = build_pipeline(model, feature_columns)

    fitted.fit(
        X_train,
        y_train,
    )

    pred = fitted.predict(
        X_2025
    )

    metrics = calculate_metrics(
        y_2025,
        pred,
    )

    district_results = test_2025[
        [
            DISTRICT_COL,
            "third_advance_estimate_2025_26_kg_ha",
        ]
    ].copy()

    district_results[
        "predicted_yield_kg_ha"
    ] = pred

    district_results[
        "abs_error_kg_ha"
    ] = np.abs(
        district_results[
            "third_advance_estimate_2025_26_kg_ha"
        ]
        - district_results[
            "predicted_yield_kg_ha"
        ]
    )

    district_results[
        "pct_error"
    ] = (
        district_results[
            "abs_error_kg_ha"
        ]
        / district_results[
            "third_advance_estimate_2025_26_kg_ha"
        ].abs()
        * 100
    )

    return fitted, metrics, district_results


# ============================================================
# MAIN EXPERIMENT
# ============================================================

def main():

    print("=" * 80)
    print("AGRIPREDICT-AI EXPERIMENTAL IMPROVEMENT STUDY")
    print("=" * 80)

    print("\nLoading production dataset...")

    df = pd.read_csv(
        DATA_PATH
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    if TARGET not in df.columns:
        raise ValueError(
            f"Target column not found: {TARGET}"
        )

    if YEAR_COL not in df.columns:
        raise ValueError(
            f"Year column not found: {YEAR_COL}"
        )

    # --------------------------------------------------------
    # Production feature schema
    # --------------------------------------------------------

    excluded = {
        TARGET,
        YEAR_COL,
        "target_source_detail",
        "target_review_flag",
        "target_note",
        "weather_temp_extraction",
        "weather_rain_extraction",
    }

    all_features = [
        c
        for c in df.columns
        if c not in excluded
    ]

    print(
        f"Feature count: {len(all_features)}"
    )

    feature_sets = build_feature_sets(
        all_features
    )

    print("\nFeature strategies:")

    for name, features in feature_sets.items():
        print(
            f"  {name}: {len(features)} features"
        )

    # --------------------------------------------------------
    # Sanity checks
    # --------------------------------------------------------

    if "district" not in all_features:
        raise ValueError(
            "district feature missing"
        )

    if len(all_features) != 36:
        raise ValueError(
            f"Expected 36 production features, "
            f"found {len(all_features)}"
        )

    # --------------------------------------------------------
    # 2025 schema validation
    # --------------------------------------------------------

    X_2025_raw = pd.read_csv(
        INPUT_2025_PATH
    )

    if list(X_2025_raw.columns) != list(
        all_features
    ):
        missing = [
            c
            for c in all_features
            if c not in X_2025_raw.columns
        ]

        extra = [
            c
            for c in X_2025_raw.columns
            if c not in all_features
        ]

        raise ValueError(
            "2025 schema mismatch.\n"
            f"Missing: {missing}\n"
            f"Extra: {extra}"
        )

    if X_2025_raw.isna().sum().sum() != 0:
        raise ValueError(
            "2025 input contains NaN values"
        )

    print(
        "\n2025 schema: EXACT MATCH"
    )

    print(
        "2025 NaN count:",
        int(
            X_2025_raw.isna().sum().sum()
        ),
    )

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------

    models = get_models()

    print("\nModels:")
    for name in models:
        print(" ", name)

    cv_summary = []
    holdout_summary = []
    hindcast_summary = []

    # --------------------------------------------------------
    # Experiment loop
    # --------------------------------------------------------

    for feature_name, features in feature_sets.items():

        print("\n" + "-" * 80)
        print(
            f"FEATURE SET: {feature_name}"
        )
        print("-" * 80)

        for model_name, model in models.items():

            experiment_name = (
                f"{feature_name}__{model_name}"
            )

            print(
                f"\nRunning: {experiment_name}"
            )

            # ------------------------------------------------
            # 2011-2023 expanding CV
            # ------------------------------------------------

            cv = expanding_window_cv(
                df=df,
                feature_columns=features,
                model=model,
                start_year=SELECTION_START_YEAR,
                end_year=2023,
            )

            if cv.empty:
                raise RuntimeError(
                    f"No CV results for {experiment_name}"
                )

            cv_mean = {
                "experiment": experiment_name,
                "feature_set": feature_name,
                "model": model_name,
                "cv_MAE_mean": cv["MAE"].mean(),
                "cv_RMSE_mean": cv["RMSE"].mean(),
                "cv_R2_mean": cv["R2"].mean(),
                "cv_MAPE_mean": cv[
                    "MAPE_percent"
                ].mean(),
                "cv_folds": len(cv),
            }

            cv_summary.append(
                cv_mean
            )

            # Save fold results
            cv_path = (
                OUTPUT_DIR
                / f"{experiment_name}__cv.csv"
            )

            cv.to_csv(
                cv_path,
                index=False,
            )

            # ------------------------------------------------
            # 2024 holdout
            # ------------------------------------------------

            fitted_2024, metrics_2024, district_2024 = (
                evaluate_2024(
                    df=df,
                    feature_columns=features,
                    model=model,
                )
            )

            holdout_summary.append(
                {
                    "experiment": experiment_name,
                    "feature_set": feature_name,
                    "model": model_name,
                    **{
                        f"2024_{k}": v
                        for k, v in metrics_2024.items()
                    },
                }
            )

            district_2024[
                "experiment"
            ] = experiment_name

            district_2024.to_csv(
                OUTPUT_DIR
                / f"{experiment_name}__2024_district.csv",
                index=False,
            )

            # ------------------------------------------------
            # 2025 hindcast
            # ------------------------------------------------

            fitted_2025, metrics_2025, district_2025 = (
                evaluate_2025(
                    df=df,
                    feature_columns=features,
                    model=model,
                )
            )

            hindcast_summary.append(
                {
                    "experiment": experiment_name,
                    "feature_set": feature_name,
                    "model": model_name,
                    **{
                        f"2025_{k}": v
                        for k, v in metrics_2025.items()
                    },
                }
            )

            district_2025[
                "experiment"
            ] = experiment_name

            district_2025.to_csv(
                OUTPUT_DIR
                / f"{experiment_name}__2025_hindcast.csv",
                index=False,
            )

            print(
                "  CV MAE:",
                round(
                    cv_mean["cv_MAE_mean"],
                    3,
                ),
            )

            print(
                "  2024 MAE:",
                round(
                    metrics_2024["MAE"],
                    3,
                ),
            )

            print(
                "  2025 MAE:",
                round(
                    metrics_2025["MAE"],
                    3,
                ),
            )

    # ========================================================
    # SUMMARY FILES
    # ========================================================

    cv_df = pd.DataFrame(
        cv_summary
    )

    holdout_df = pd.DataFrame(
        holdout_summary
    )

    hindcast_df = pd.DataFrame(
        hindcast_summary
    )

    cv_df.to_csv(
        OUTPUT_DIR / "cv_summary.csv",
        index=False,
    )

    holdout_df.to_csv(
        OUTPUT_DIR / "2024_holdout_summary.csv",
        index=False,
    )

    hindcast_df.to_csv(
        OUTPUT_DIR / "2025_hindcast_summary.csv",
        index=False,
    )

    # ========================================================
    # COMBINED SUMMARY
    # ========================================================

    combined = cv_df.merge(
        holdout_df,
        on=[
            "experiment",
            "feature_set",
            "model",
        ],
        how="inner",
    )

    combined = combined.merge(
        hindcast_df,
        on=[
            "experiment",
            "feature_set",
            "model",
        ],
        how="inner",
    )

    combined.to_csv(
        OUTPUT_DIR
        / "experimental_comparison.csv",
        index=False,
    )

    # ========================================================
    # RANKING FOR INFORMATION ONLY
    # ========================================================

    # This is NOT a production model selection.
    # It is only an experimental table for inspection.

    ranking = combined.sort_values(
        by=[
            "2025_MAE",
            "2024_MAE",
        ],
        ascending=[
            True,
            True,
        ],
    )

    ranking.to_csv(
        OUTPUT_DIR
        / "experimental_comparison_sorted_for_inspection.csv",
        index=False,
    )

    # ========================================================
    # METADATA
    # ========================================================

    metadata = {
        "dataset": str(DATA_PATH),
        "target": TARGET,
        "training_period_for_2024": "1997-2023",
        "selection_validation_period": "2011-2023",
        "holdout_year": 2024,
        "experimental_hindcast_year": 2025,
        "production_model_modified": False,
        "production_artifact_overwritten": False,
        "yavatmal_retained": True,
        "num_production_features": len(all_features),
        "num_2025_rows": len(X_2025_raw),
        "2025_schema_exact_match": True,
        "2025_weather_type": (
            "Observed full-year weather; "
            "end-of-season hindcast"
        ),
        "note": (
            "2025 benchmark is the official "
            "Third Advance Estimate and is not "
            "treated as a prospective pre-season forecast."
        ),
    }

    with open(
        OUTPUT_DIR / "experiment_metadata.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)

    print(
        "\nResults saved to:"
    )

    print(
        OUTPUT_DIR
    )

    print(
        "\nProduction model was NOT modified."
    )

    print(
        "Production final_model.pkl was NOT overwritten."
    )

    print(
        "\nMain comparison file:"
    )

    print(
        OUTPUT_DIR
        / "experimental_comparison.csv"
    )


if __name__ == "__main__":
    main()
