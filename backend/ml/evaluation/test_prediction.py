import os
import sys
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_ROOT = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(ML_ROOT)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "vidarbha_cotton_model_ready_1997_2024.csv")

TARGET_COL = "yield_target_kg_ha"
EXCLUDE_COLS = [
    "yield_target_kg_ha", "target_source_detail", "target_review_flag", 
    "target_note", "weather_temp_extraction", "weather_rain_extraction", "year"
]
CATEGORICAL_COLS = ["district"]

def run_test():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    
    feature_cols = [c for c in df.columns if c not in EXCLUDE_COLS]
    cat_cols = [c for c in feature_cols if c in CATEGORICAL_COLS]
    num_cols = [c for c in feature_cols if c not in CATEGORICAL_COLS]

    train_df = df[df["year"] < 2024].copy()
    test_2024 = df[df["year"] == 2024].copy()

    X_train = train_df[feature_cols]
    y_train = train_df[TARGET_COL].values
    X_test = test_2024[feature_cols]
    y_test = test_2024[TARGET_COL].values

    num_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    cat_transformer = Pipeline([("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    preprocessor = ColumnTransformer(transformers=[("num", num_transformer, num_cols), ("cat", cat_transformer, cat_cols)])
    
    val_model = Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42))
    ])
    
    val_model.fit(X_train, y_train)
    preds_2024 = val_model.predict(X_test)

    print("=" * 90)
    print("AGRIPREDICT-AI 2024 HOLDOUT PREDICTION TEST (Trained ONLY on 1997–2023)")
    print("=" * 90)
    print(f"{'District':<12} | {'Rainfall(mm)':<12} | {'Temp(°C)':<9} | {'Actual(kg/ha)':<14} | {'Predicted(kg/ha)':<17} | {'Error(kg/ha)':<13} | {'Error %':<8}")
    print("-" * 90)

    for idx, row in test_2024.iterrows():
        loc = test_2024.index.get_loc(idx)
        dist = row["district"]
        rain = round(row["rainfall_annual_mm"], 1)
        temp = round(row["tmax_kharif_mean_c"], 1)
        act = round(float(row[TARGET_COL]), 1)
        pred = round(float(preds_2024[loc]), 1)
        err = round(abs(act - pred), 1)
        pct = round((err / act) * 100, 2) if act != 0 else 0.0

        print(f"{dist:<12} | {rain:<12} | {temp:<9} | {act:<14} | {pred:<17} | {err:<13} | {pct:<8}%")

    print("-" * 90)
    mae = np.mean(np.abs(y_test - preds_2024))
    rmse = np.sqrt(np.mean((y_test - preds_2024)**2))
    print(f"Overall 2024 Holdout MAE:  {mae:.2f} kg/ha")
    print(f"Overall 2024 Holdout RMSE: {rmse:.2f} kg/ha")
    print("=" * 90)

if __name__ == "__main__":
    run_test()
