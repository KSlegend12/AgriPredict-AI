import os
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer


# ============================================================
# CONFIG
# ============================================================

DATA_PATH = "backend/data/vidarbha_cotton_model_ready_1997_2024.csv"

OUTPUT_DIR = "backend/ml/evaluation/experimental_rf_temporal_validation"

TARGET = "yield_target_kg_ha"
YEAR_COL = "year"
DISTRICT_COL = "district"

FEATURE_COLUMNS = [
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
# HELPERS
# ============================================================

def build_pipeline(model):
    numeric_features = [
        c for c in FEATURE_COLUMNS
        if c != DISTRICT_COL
    ]

    categorical_features = [DISTRICT_COL]

    preprocessor = ColumnTransformer(
        transformers=[
           (
    "num",
    Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    ),
    numeric_features,
),
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def safe_mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mask = y_true != 0

    if not np.any(mask):
        return np.nan

    return np.mean(
        np.abs(
            (y_true[mask] - y_pred[mask])
            / y_true[mask]
        )
    ) * 100.0


def evaluate(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)

    rmse = np.sqrt(
        mean_squared_error(y_true, y_pred)
    )

    r2 = r2_score(y_true, y_pred)

    mape = safe_mape(y_true, y_pred)

    return {
        "MAE_kg_ha": mae,
        "RMSE_kg_ha": rmse,
        "R2": r2,
        "MAPE_percent": mape,
        "MAPE_derived_score": 100.0 - mape,
    }


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("RANDOMFOREST vs GRADIENTBOOSTING")
print("CHRONOLOGICAL TEMPORAL VALIDATION")
print("=" * 80)

df = pd.read_csv(DATA_PATH)

print("\nDataset shape:", df.shape)

required_columns = (
    FEATURE_COLUMNS
    + [TARGET, YEAR_COL]
)

missing = [
    c for c in required_columns
    if c not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

df = df.sort_values(
    [YEAR_COL, DISTRICT_COL]
).reset_index(drop=True)

years = sorted(
    df[YEAR_COL].unique()
)

print(
    "Available years:",
    years[0],
    "-",
    years[-1]
)

print(
    "Validation years:",
    2011,
    "-",
    2024
)


# ============================================================
# MODELS
# ============================================================

models = {
    "GradientBoosting": GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    ),

    "RandomForest": RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        max_features=1.0,
    ),
}


# ============================================================
# TEMPORAL VALIDATION
# ============================================================

all_results = []
district_results = []

for validation_year in range(2011, 2025):

    train_df = df[
        df[YEAR_COL] < validation_year
    ].copy()

    valid_df = df[
        df[YEAR_COL] == validation_year
    ].copy()

    if train_df.empty or valid_df.empty:
        continue

    print("\n" + "-" * 80)
    print(
        f"VALIDATION YEAR: {validation_year}"
    )

    print(
        f"Training: {train_df[YEAR_COL].min()}-"
        f"{train_df[YEAR_COL].max()}"
    )

    print(
        "Training rows:",
        len(train_df)
    )

    print(
        "Validation rows:",
        len(valid_df)
    )

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET]

    X_valid = valid_df[FEATURE_COLUMNS]
    y_valid = valid_df[TARGET]

    for model_name, base_model in models.items():

        print(
            f"\n{model_name}: training..."
        )

        model = build_pipeline(
            clone(base_model)
        )

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_valid
        )

        metrics = evaluate(
            y_valid,
            predictions
        )

        print(
            f"MAE  : {metrics['MAE_kg_ha']:.4f}"
        )

        print(
            f"RMSE : {metrics['RMSE_kg_ha']:.4f}"
        )

        print(
            f"R2   : {metrics['R2']:.4f}"
        )

        print(
            f"MAPE : {metrics['MAPE_percent']:.4f}%"
        )

        result = {
            "validation_year": validation_year,
            "train_start_year": int(
                train_df[YEAR_COL].min()
            ),
            "train_end_year": int(
                train_df[YEAR_COL].max()
            ),
            "model": model_name,
            "train_rows": len(train_df),
            "validation_rows": len(valid_df),
            **metrics,
        }

        all_results.append(result)

        for district, actual, predicted in zip(
            valid_df[DISTRICT_COL],
            y_valid,
            predictions,
        ):

            district_results.append({
                "validation_year": validation_year,
                "model": model_name,
                "district": district,
                "actual_kg_ha": actual,
                "predicted_kg_ha": predicted,
                "error_kg_ha": actual - predicted,
                "abs_error_kg_ha": abs(
                    actual - predicted
                ),
                "pct_error": (
                    abs(actual - predicted)
                    / abs(actual)
                    * 100
                    if actual != 0
                    else np.nan
                ),
            })


# ============================================================
# SAVE RESULTS
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

results_df = pd.DataFrame(
    all_results
)

district_df = pd.DataFrame(
    district_results
)

results_path = os.path.join(
    OUTPUT_DIR,
    "temporal_validation_model_results.csv"
)

district_path = os.path.join(
    OUTPUT_DIR,
    "temporal_validation_district_results.csv"
)

results_df.to_csv(
    results_path,
    index=False
)

district_df.to_csv(
    district_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

summary = (
    results_df
    .groupby("model")
    [
        [
            "MAE_kg_ha",
            "RMSE_kg_ha",
            "R2",
            "MAPE_percent",
            "MAPE_derived_score",
        ]
    ]
    .agg(["mean", "std"])
)

print("\n")
print("=" * 80)
print("TEMPORAL VALIDATION SUMMARY")
print("=" * 80)

print(
    summary.to_string()
)

print("\n")
print("=" * 80)
print("YEAR-BY-YEAR MAE")
print("=" * 80)

mae_table = results_df.pivot(
    index="validation_year",
    columns="model",
    values="MAE_kg_ha",
)

print(
    mae_table.to_string()
)

print("\n")
print("=" * 80)
print("RESULTS SAVED")
print("=" * 80)

print(results_path)
print(district_path)

print("\nProduction model was NOT modified.")
print("Production artifact was NOT overwritten.")