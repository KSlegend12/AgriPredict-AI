"""
AgriPredict-AI
Experimental 2025 Out-of-Sample Evaluation

Experiment:
    Train: 1997-2024
    Test:  2025

IMPORTANT:
- 2025 target is NEVER used for training.
- Production model is NOT modified.
- final_model.pkl is NOT overwritten.
- Yavatmal is retained.
- 2025 is treated as an unseen test year.
"""

from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
    HistGradientBoostingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT
    / "backend"
    / "data"
    / "vidarbha_cotton_model_ready_1997_2024.csv"
)

INPUT_2025_PATH = (
    ROOT
    / "data"
    / "cotton_2025_experimental_model_input.csv"
)

TARGET_2025_PATH = (
    ROOT
    / "data"
    / "cotton_2025_experimental_predictions.csv"
)

OUTPUT_DIR = (
    ROOT
    / "backend"
    / "ml"
    / "evaluation"
    / "experimental_2025_train_to_2024"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CONFIG
# ============================================================

TARGET = "yield_target_kg_ha"
YEAR_COL = "year"
DISTRICT_COL = "district"

TRAIN_END_YEAR = 2024
TEST_YEAR = 2025

RANDOM_STATE = 42


# ============================================================
# PRODUCTION 36 FEATURES
# ============================================================

FEATURES = [
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


# ============================================================
# MODELS
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
# PREPROCESSING
# ============================================================

def build_pipeline(model):

    numerical_features = [
        c
        for c in FEATURES
        if c != DISTRICT_COL
    ]

    categorical_features = [
        DISTRICT_COL
    ]

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            )
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
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
                numerical_features,
            ),
            (
                "cat",
                categorical_pipeline,
                categorical_features,
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
# METRICS
# ============================================================

def calculate_metrics(
    y_true,
    y_pred,
):

    y_true = np.asarray(
        y_true,
        dtype=float,
    )

    y_pred = np.asarray(
        y_pred,
        dtype=float,
    )

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )

    r2 = r2_score(
        y_true,
        y_pred,
    )

    non_zero = (
        np.abs(y_true) > 1e-12
    )

    if np.any(non_zero):

        mape = (
            np.mean(
                np.abs(
                    (
                        y_true[non_zero]
                        - y_pred[non_zero]
                    )
                    / y_true[non_zero]
                )
            )
            * 100
        )

    else:

        mape = np.nan

    return {
        "MAE_kg_ha": float(mae),
        "RMSE_kg_ha": float(rmse),
        "R2": float(r2),
        "MAPE_percent": float(mape),
        "MAPE_derived_score": float(
            100 - mape
        ),
    }


# ============================================================
# LOAD 2025 DATA
# ============================================================

def load_2025_test_data():

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
            "Missing 2025 target columns: "
            + str(sorted(missing))
        )

    # --------------------------------------------------------
    # Exact feature schema check
    # --------------------------------------------------------

    missing_features = [
        c
        for c in FEATURES
        if c not in X_2025.columns
    ]

    extra_features = [
        c
        for c in X_2025.columns
        if c not in FEATURES
    ]

    if missing_features or extra_features:

        raise ValueError(
            "\n2025 schema mismatch!"
            f"\nMissing: {missing_features}"
            f"\nExtra: {extra_features}"
        )

    X_2025 = X_2025[
        FEATURES
    ].copy()

    # --------------------------------------------------------
    # No target allowed inside X
    # --------------------------------------------------------

    if TARGET in X_2025.columns:

        raise ValueError(
            "TARGET LEAKAGE: "
            "2025 target found inside model input!"
        )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    nan_count = int(
        X_2025.isna()
        .sum()
        .sum()
    )

    if nan_count != 0:

        raise ValueError(
            f"2025 model input contains "
            f"{nan_count} NaN values"
        )

    # --------------------------------------------------------
    # Merge target separately
    # --------------------------------------------------------

    target_2025 = target_2025[
        [
            DISTRICT_COL,
            "third_advance_estimate_2025_26_kg_ha",
        ]
    ].copy()

    merged = X_2025.merge(
        target_2025,
        on=DISTRICT_COL,
        how="inner",
        validate="one_to_one",
    )

    if len(merged) != 7:

        raise ValueError(
            f"Expected 7 districts, "
            f"got {len(merged)}"
        )

    return merged


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "2025 OUT-OF-SAMPLE EXPERIMENT"
    )
    print("=" * 80)

    print(
        "\nTRAINING PERIOD:"
    )

    print(
        "1997-2024"
    )

    print(
        "\nTEST PERIOD:"
    )

    print(
        "2025"
    )

    # ========================================================
    # Load historical data
    # ========================================================

    df = pd.read_csv(
        DATA_PATH
    )

    print(
        "\nHistorical dataset:",
        df.shape,
    )

    # --------------------------------------------------------
    # Verify required columns
    # --------------------------------------------------------

    missing = [
        c
        for c in FEATURES + [
            TARGET,
            YEAR_COL,
        ]
        if c not in df.columns
    ]

    if missing:

        raise ValueError(
            "Historical dataset missing columns: "
            + str(missing)
        )

    # ========================================================
    # Training data = 1997-2024
    # ========================================================

    train_df = df[
        df[YEAR_COL] <= TRAIN_END_YEAR
    ].copy()

    if train_df[YEAR_COL].max() != 2024:

        raise ValueError(
            "Training data does not end at 2024."
        )

    if train_df[YEAR_COL].min() != 1997:

        raise ValueError(
            "Training data does not start at 1997."
        )

    print(
        "\nTraining rows:",
        len(train_df),
    )

    print(
        "Training years:",
        train_df[YEAR_COL].min(),
        "-",
        train_df[YEAR_COL].max(),
    )

    # ========================================================
    # Load 2025
    # ========================================================

    test_2025 = load_2025_test_data()

    print(
        "\n2025 test rows:",
        len(test_2025),
    )

    print(
        "2025 districts:"
    )

    print(
        test_2025[DISTRICT_COL]
        .tolist()
    )

    # ========================================================
    # Critical leakage check
    # ========================================================

    print(
        "\nChecking target leakage..."
    )

    if (
        "third_advance_estimate_2025_26_kg_ha"
        in FEATURES
    ):

        raise ValueError(
            "2025 target is inside FEATURES!"
        )

    if TARGET in FEATURES:

        raise ValueError(
            "Production target is inside FEATURES!"
        )

    print(
        "Target leakage check: PASS"
    )

    # ========================================================
    # Prepare X / y
    # ========================================================

    X_train = train_df[
        FEATURES
    ].copy()

    y_train = train_df[
        TARGET
    ].copy()

    X_test = test_2025[
        FEATURES
    ].copy()

    y_test = test_2025[
        "third_advance_estimate_2025_26_kg_ha"
    ].copy()

    # ========================================================
    # Train all candidate models
    # ========================================================

    models = get_models()

    all_results = []
    district_results = []

    for model_name, model in models.items():

        print(
            "\n" + "-" * 80
        )

        print(
            "MODEL:",
            model_name,
        )

        pipeline = build_pipeline(
            model
        )

        print(
            "Training on 1997-2024..."
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        print(
            "Predicting unseen 2025..."
        )

        predictions = pipeline.predict(
            X_test
        )

        metrics = calculate_metrics(
            y_test,
            predictions,
        )

        print(
            "\n2025 Metrics:"
        )

        print(
            "MAE :",
            round(
                metrics[
                    "MAE_kg_ha"
                ],
                4,
            ),
            "kg/ha",
        )

        print(
            "RMSE:",
            round(
                metrics[
                    "RMSE_kg_ha"
                ],
                4,
            ),
            "kg/ha",
        )

        print(
            "R2  :",
            round(
                metrics["R2"],
                4,
            ),
        )

        print(
            "MAPE:",
            round(
                metrics[
                    "MAPE_percent"
                ],
                4,
            ),
            "%",
        )

        print(
            "100-MAPE:",
            round(
                metrics[
                    "MAPE_derived_score"
                ],
                4,
            ),
            "%",
        )

        # ----------------------------------------------------
        # Overall result
        # ----------------------------------------------------

        all_results.append(
            {
                "model": model_name,
                "train_start_year": 1997,
                "train_end_year": 2024,
                "test_year": 2025,
                **metrics,
            }
        )

        # ----------------------------------------------------
        # District results
        # ----------------------------------------------------

        for i, district in enumerate(
            test_2025[
                DISTRICT_COL
            ]
        ):

            actual = float(
                y_test.iloc[i]
            )

            predicted = float(
                predictions[i]
            )

            abs_error = abs(
                actual
                - predicted
            )

            pct_error = (
                abs_error
                / abs(actual)
                * 100
                if actual != 0
                else np.nan
            )

            district_results.append(
                {
                    "model": model_name,
                    "district": district,
                    "actual_2025_kg_ha": actual,
                    "predicted_2025_kg_ha": predicted,
                    "error_kg_ha": (
                        predicted
                        - actual
                    ),
                    "abs_error_kg_ha": abs_error,
                    "pct_error": pct_error,
                }
            )

    # ========================================================
    # Save overall results
    # ========================================================

    results_df = pd.DataFrame(
        all_results
    )

    results_df = results_df.sort_values(
        "MAE_kg_ha"
    )

    results_path = (
        OUTPUT_DIR
        / "2025_out_of_sample_model_comparison.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    # ========================================================
    # Save district results
    # ========================================================

    district_df = pd.DataFrame(
        district_results
    )

    district_path = (
        OUTPUT_DIR
        / "2025_out_of_sample_district_results.csv"
    )

    district_df.to_csv(
        district_path,
        index=False,
    )

    # ========================================================
    # Save metadata
    # ========================================================

    metadata = {

        "experiment":
            "2025_out_of_sample",

        "training_start":
            1997,

        "training_end":
            2024,

        "test_year":
            2025,

        "target":
            TARGET,

        "2025_target_column":
            "third_advance_estimate_2025_26_kg_ha",

        "num_training_rows":
            int(len(train_df)),

        "num_test_rows":
            int(len(test_2025)),

        "num_features":
            len(FEATURES),

        "target_used_in_2025_training":
            False,

        "production_model_modified":
            False,

        "production_artifact_overwritten":
            False,

        "yavatmal_included":
            "Yavatmal"
            in test_2025[
                DISTRICT_COL
            ].values,

        "2025_evaluation_type":
            "End-of-season out-of-sample hindcast",

        "weather_note":
            "2025 model input uses the prepared "
            "experimental 2025 feature dataset.",

        "metric_note":
            "100-MAPE is reported only as a "
            "MAPE-derived score, not standard "
            "classification accuracy.",
    }

    metadata_path = (
        OUTPUT_DIR
        / "experiment_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metadata,
            f,
            indent=2,
        )

    # ========================================================
    # Final output
    # ========================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "2025 OUT-OF-SAMPLE EXPERIMENT COMPLETE"
    )

    print(
        "=" * 80
    )

    print(
        "\nModel comparison:"
    )

    print(
        results_df[
            [
                "model",
                "MAE_kg_ha",
                "RMSE_kg_ha",
                "R2",
                "MAPE_percent",
                "MAPE_derived_score",
            ]
        ].to_string(
            index=False
        )
    )

    print(
        "\nResults saved:"
    )

    print(
        results_path
    )

    print(
        district_path
    )

    print(
        "\nProduction model was NOT modified."
    )

    print(
        "Production artifact was NOT overwritten."
    )


if __name__ == "__main__":
    main()