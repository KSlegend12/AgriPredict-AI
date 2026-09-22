from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path.cwd()
BASE = ROOT / "backend/ml/future_forecasting/data_audit/forecast_origin_safe_feature_rows.csv"
SMAP = ROOT / "backend/ml/future_forecasting/data_audit/forecast_origin_safe_smap_features.csv"
OUT = ROOT / "backend/ml/future_forecasting/data_audit"

base = pd.read_csv(BASE)
smap = pd.read_csv(SMAP)

SMAP_FEATURES = [
    c for c in smap.columns
    if c.startswith("sm_") and not c.endswith("_valid_obs")
]

BASE_FEATURES = [c for c in base.columns if c != "actual"]

# Use only the 196 rows for which origin-year SMAP exists.
KEYS = ["district", "target_year", "horizon"]

exp = base.merge(
    smap[KEYS + SMAP_FEATURES],
    on=KEYS,
    how="inner",
    validate="one_to_one"
)

print("Base rows:", len(base))
print("SMAP experiment rows:", len(exp))
print("SMAP features:", len(SMAP_FEATURES))

if len(exp) != 196:
    raise RuntimeError(f"Expected 196 SMAP rows, got {len(exp)}")

if exp[SMAP_FEATURES].isna().sum().sum() != 0:
    raise RuntimeError("SMAP features contain missing values")

if exp.duplicated(KEYS).any():
    raise RuntimeError("Duplicate district-target-horizon rows found")

models = {
    "Ridge": lambda features: Pipeline([
        ("prep", ColumnTransformer([
            ("num", Pipeline([
                ("imp", SimpleImputer(strategy="median")),
                ("sc", StandardScaler())
            ]), [c for c in features if c != "district"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["district"])
        ])),
        ("model", Ridge(alpha=10.0))
    ]),
    "RandomForest": lambda features: Pipeline([
        ("prep", ColumnTransformer([
            ("num", SimpleImputer(strategy="median"),
             [c for c in features if c != "district"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["district"])
        ])),
        ("model", RandomForestRegressor(
            n_estimators=50,
            max_depth=6,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=4
        ))
    ]),
    "GradientBoosting": lambda features: Pipeline([
        ("prep", ColumnTransformer([
            ("num", SimpleImputer(strategy="median"),
             [c for c in features if c != "district"]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["district"])
        ])),
        ("model", GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        ))
    ])
}

results = []

for feature_set_name, features in [
    ("BASE", BASE_FEATURES),
    ("BASE_PLUS_SMAP", BASE_FEATURES + SMAP_FEATURES)
]:
    for h in range(1, 8):
        for t in range(2015, 2025):

            train = exp[
                (exp.target_year < t) &
                (exp.horizon == h)
            ]

            test = exp[
                (exp.target_year == t) &
                (exp.horizon == h)
            ]

            if len(train) < 30 or test.empty:
                continue

            for model_name, make_model in models.items():
                model = make_model(features)
                model.fit(train[features], train.actual)
                pred = model.predict(test[features])

                for (_, row), p in zip(test.iterrows(), pred):
                    results.append({
                        "feature_set": feature_set_name,
                        "model": model_name,
                        "horizon": h,
                        "target_year": t,
                        "origin_year": int(t - h),
                        "district": row.district,
                        "actual": row.actual,
                        "prediction": float(p)
                    })

pred = pd.DataFrame(results)

pred.to_csv(
    OUT / "smap_controlled_hindcast_predictions.csv",
    index=False
)

summary = []

for (feature_set, model, h), g in pred.groupby(
    ["feature_set", "model", "horizon"]
):
    summary.append({
        "feature_set": feature_set,
        "model": model,
        "horizon": h,
        "n": len(g),
        "mae_kg_ha": mean_absolute_error(
            g.actual, g.prediction
        ),
        "rmse_kg_ha": mean_squared_error(
            g.actual, g.prediction
        ) ** 0.5
    })

summary = pd.DataFrame(summary).sort_values(
    ["horizon", "model", "feature_set"]
)

summary.to_csv(
    OUT / "smap_controlled_hindcast_summary.csv",
    index=False
)

print("\n=== CONTROLLED SMAP HINDCAST ===")
print(summary.to_string(index=False))
