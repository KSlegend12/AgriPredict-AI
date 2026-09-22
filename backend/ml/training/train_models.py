"""
AgriPredict-AI: Authoritative Machine Learning Pipeline for Vidarbha Cotton Yield Prediction

Districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim, Yavatmal
Years: 1997–2024
Authoritative Dataset: vidarbha_cotton_model_ready_1997_2024.csv
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance
import joblib

# Models
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)
import xgboost as xgb

# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_ROOT = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(ML_ROOT)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "vidarbha_cotton_model_ready_1997_2024.csv")
ARTIFACTS_DIR = os.path.join(ML_ROOT, "artifacts")
PLOTS_DIR = os.path.join(ML_ROOT, "evaluation", "plots")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# Set seeds for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ---------------------------------------------------------
# FEATURE CLASSIFICATION
# ---------------------------------------------------------
TARGET_COL = "yield_target_kg_ha"

# Metadata / Target-derived columns to exclude from training features
EXCLUDE_COLS = [
    "yield_target_kg_ha",
    "target_source_detail",
    "target_review_flag",
    "target_note",
    "weather_temp_extraction",
    "weather_rain_extraction",
    "year"  # Used for temporal splitting, not as a predictive feature
]

CATEGORICAL_COLS = ["district"]

# ---------------------------------------------------------
# HELPER METRIC FUNCTION
# ---------------------------------------------------------
def compute_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return {"MAE": mae, "RMSE": rmse, "R2": r2}

# ---------------------------------------------------------
# PIPELINE BUILDER
# ---------------------------------------------------------
def create_model_pipeline(model_name, model_instance, num_cols, cat_cols):
    """
    Builds a scikit-learn Pipeline with fitted-on-train-only preprocessing.
    """
    if model_name == "Ridge":
        num_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
    else:
        # Tree-based models don't require feature scaling
        num_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median"))
        ])

    cat_transformer = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_cols),
            ("cat", cat_transformer, cat_cols)
        ]
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model_instance)
    ])

    return pipeline

# ---------------------------------------------------------
# TEMPORAL VALIDATION ENGINE
# ---------------------------------------------------------
def run_temporal_validation(df, feature_cols, num_cols, cat_cols, models_dict):
    """
    Performs expanding-window temporal validation from 2011 to 2024.
    Preventing temporal data leakage.
    """
    test_years = sorted([y for y in df["year"].unique() if y >= 2011])
    print(f"\n--- Running Temporal Validation over {len(test_years)} test folds (Years: {min(test_years)}–{max(test_years)}) ---")

    # Store per-fold results
    validation_records = []
    predictions_records = []

    # 1. EVALUATE BASELINES FIRST
    for test_year in test_years:
        train_df = df[df["year"] < test_year]
        test_df = df[df["year"] == test_year]

        y_test = test_df[TARGET_COL].values

        # Baseline 1: Previous Year Yield (lag 1 column)
        # Fall back to training set median if previous_year_yield_kg_ha is NaN
        prev_year_preds = test_df["previous_year_yield_kg_ha"].fillna(train_df[TARGET_COL].median()).values
        b1_metrics = compute_metrics(y_test, prev_year_preds)
        
        for idx, row in test_df.iterrows():
            predictions_records.append({
                "model": "Baseline_PrevYear",
                "test_year": test_year,
                "district": row["district"],
                "actual": row[TARGET_COL],
                "predicted": prev_year_preds[test_df.index.get_loc(idx)]
            })

        validation_records.append({
            "model": "Baseline_PrevYear",
            "test_year": test_year,
            "MAE": b1_metrics["MAE"],
            "RMSE": b1_metrics["RMSE"],
            "R2": b1_metrics["R2"]
        })

        # Baseline 2: Historical District Mean (Expanding mean up to test_year - 1)
        dist_means = train_df.groupby("district")[TARGET_COL].mean()
        mean_preds = test_df["district"].map(dist_means).fillna(train_df[TARGET_COL].mean()).values
        b2_metrics = compute_metrics(y_test, mean_preds)

        for idx, row in test_df.iterrows():
            predictions_records.append({
                "model": "Baseline_HistMean",
                "test_year": test_year,
                "district": row["district"],
                "actual": row[TARGET_COL],
                "predicted": mean_preds[test_df.index.get_loc(idx)]
            })

        validation_records.append({
            "model": "Baseline_HistMean",
            "test_year": test_year,
            "MAE": b2_metrics["MAE"],
            "RMSE": b2_metrics["RMSE"],
            "R2": b2_metrics["R2"]
        })

    # 2. EVALUATE ML MODELS
    for model_name, model_instance in models_dict.items():
        print(f"Evaluating model: {model_name}...")
        for test_year in test_years:
            train_df = df[df["year"] < test_year]
            test_df = df[df["year"] == test_year]

            X_train = train_df[feature_cols]
            y_train = train_df[TARGET_COL].values
            X_test = test_df[feature_cols]
            y_test = test_df[TARGET_COL].values

            pipeline = create_model_pipeline(model_name, model_instance, num_cols, cat_cols)
            pipeline.fit(X_train, y_train)
            preds = pipeline.predict(X_test)

            metrics = compute_metrics(y_test, preds)

            validation_records.append({
                "model": model_name,
                "test_year": test_year,
                "MAE": metrics["MAE"],
                "RMSE": metrics["RMSE"],
                "R2": metrics["R2"]
            })

            for idx, row in test_df.iterrows():
                predictions_records.append({
                    "model": model_name,
                    "test_year": test_year,
                    "district": row["district"],
                    "actual": row[TARGET_COL],
                    "predicted": preds[test_df.index.get_loc(idx)]
                })

    val_df = pd.DataFrame(validation_records)
    preds_df = pd.DataFrame(predictions_records)
    return val_df, preds_df

# ---------------------------------------------------------
# SUMMARY METRICS & MODEL COMPARISON
# ---------------------------------------------------------
def summarize_results(val_df):
    summary = val_df.groupby("model").agg(
        Mean_MAE=("MAE", "mean"),
        Std_MAE=("MAE", "std"),
        Mean_RMSE=("RMSE", "mean"),
        Std_RMSE=("RMSE", "std"),
        Mean_R2=("R2", "mean"),
        Std_R2=("R2", "std")
    ).reset_index()

    # Sort by Mean MAE ascending
    summary = summary.sort_values(by="Mean_MAE", ascending=True).reset_index(drop=True)
    return summary

# ---------------------------------------------------------
# MAIN EXECUTION PIPELINE
# ---------------------------------------------------------
def main():
    print("=" * 80)
    print("AGRIPREDICT-AI: COTTON YIELD ML PIPELINE EXECUTION")
    print("=" * 80)

    # Load dataset
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset from: {DATA_PATH} ({df.shape[0]} rows, {df.shape[1]} cols)")

    # Identify feature columns
    feature_cols = [c for c in df.columns if c not in EXCLUDE_COLS]
    cat_cols = [c for c in feature_cols if c in CATEGORICAL_COLS]
    num_cols = [c for c in feature_cols if c not in CATEGORICAL_COLS]

    print(f"\nTotal Predictive Features: {len(feature_cols)}")
    print(f"  - Categorical ({len(cat_cols)}): {cat_cols}")
    print(f"  - Numerical ({len(num_cols)}): {len(num_cols)} features")

    # Define Candidate Models
    models = {
        "Ridge": Ridge(alpha=10.0, random_state=RANDOM_STATE),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=RANDOM_STATE),
        "ExtraTrees": ExtraTreesRegressor(n_estimators=100, max_depth=6, random_state=RANDOM_STATE),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=RANDOM_STATE),
        "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=100, learning_rate=0.05, max_depth=3, random_state=RANDOM_STATE),
        "XGBoost": xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=RANDOM_STATE, eval_metric="rmse")
    }

    # Run Temporal Cross-Validation
    val_df, preds_df = run_temporal_validation(df, feature_cols, num_cols, cat_cols, models)

    # Summarize Results
    summary_df = summarize_results(val_df)
    print("\n" + "=" * 80)
    print("MODEL COMPARISON SUMMARY (Across Temporal Test Splits 2011–2024)")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    print("=" * 80)

    # Select Best Model
    best_model_name = summary_df.iloc[0]["model"]
    best_mean_mae = summary_df.iloc[0]["Mean_MAE"]
    best_mean_rmse = summary_df.iloc[0]["Mean_RMSE"]
    best_mean_r2 = summary_df.iloc[0]["Mean_R2"]

    print(f"\n>>> BEST SELECTED MODEL: {best_model_name} <<<")
    print(f"    Mean Validation MAE:  {best_mean_mae:.2f} kg/ha")
    print(f"    Mean Validation RMSE: {best_mean_rmse:.2f} kg/ha")
    print(f"    Mean Validation R²:   {best_mean_r2:.4f}")

    # Retrain Best Model on Full Dataset
    print(f"\nRetraining final model ({best_model_name}) on full 1997–2024 historical dataset...")
    best_instance = models[best_model_name]
    final_pipeline = create_model_pipeline(best_model_name, best_instance, num_cols, cat_cols)
    
    X_full = df[feature_cols]
    y_full = df[TARGET_COL].values
    final_pipeline.fit(X_full, y_full)

    # Extract feature names after OneHotEncoding
    ohe_categories = final_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"].get_feature_names_out(cat_cols)
    transformed_feature_names = num_cols + list(ohe_categories)

    # Calculate Feature Importance / Permutation Importance
    print("\nCalculating Feature Importances...")
    if hasattr(final_pipeline.named_steps["model"], "feature_importances_"):
        raw_importances = final_pipeline.named_steps["model"].feature_importances_
        fi_df = pd.DataFrame({
            "feature": transformed_feature_names,
            "importance": raw_importances
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)
    else:
        # Permutation importance fallback
        perm_imp = permutation_importance(final_pipeline, X_full, y_full, n_repeats=10, random_state=RANDOM_STATE)
        fi_df = pd.DataFrame({
            "feature": feature_cols,
            "importance": perm_imp.importances_mean
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)

    print("\nTop 15 Most Important Predictive Features:")
    print(fi_df.head(15).to_string(index=False))

    # ---------------------------------------------------------
    # SAVE ARTIFACTS
    # ---------------------------------------------------------
    model_artifact_path = os.path.join(ARTIFACTS_DIR, "final_cotton_yield_model.joblib")
    joblib.dump(final_pipeline, model_artifact_path)
    print(f"\nSaved final trained pipeline to: {model_artifact_path}")

    # Save feature names & metadata
    metadata = {
        "model_name": best_model_name,
        "target_col": TARGET_COL,
        "feature_cols": feature_cols,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "transformed_feature_names": transformed_feature_names,
        "training_years": "1997-2024",
        "num_rows": len(df),
        "validation_metrics": {
            "Mean_MAE": float(best_mean_mae),
            "Std_MAE": float(summary_df.iloc[0]["Std_MAE"]),
            "Mean_RMSE": float(best_mean_rmse),
            "Std_RMSE": float(summary_df.iloc[0]["Std_RMSE"]),
            "Mean_R2": float(best_mean_r2),
            "Std_R2": float(summary_df.iloc[0]["Std_R2"])
        },
        "all_models_summary": summary_df.to_dict(orient="records")
    }

    metadata_path = os.path.join(ARTIFACTS_DIR, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to: {metadata_path}")

    fi_path = os.path.join(ARTIFACTS_DIR, "feature_importance.json")
    fi_df.to_json(fi_path, orient="records", indent=2)
    print(f"Saved feature importances to: {fi_path}")

    # ---------------------------------------------------------
    # GENERATE & SAVE PLOTS
    # ---------------------------------------------------------
    print("\nGenerating Evaluation Plots...")
    best_preds_df = preds_df[preds_df["model"] == best_model_name]

    # Plot 1: Actual vs Predicted
    plt.figure(figsize=(8, 6))
    plt.scatter(best_preds_df["actual"], best_preds_df["predicted"], alpha=0.7, color="teal", edgecolors="k")
    min_val = min(best_preds_df["actual"].min(), best_preds_df["predicted"].min())
    max_val = max(best_preds_df["actual"].max(), best_preds_df["predicted"].max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label="Perfect 1:1 Line")
    plt.xlabel("Actual Cotton Yield (kg/ha)")
    plt.ylabel("Predicted Cotton Yield (kg/ha)")
    plt.title(f"Actual vs Predicted Yield ({best_model_name} — Temporal Out-of-Sample Folds)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p1 = os.path.join(PLOTS_DIR, "actual_vs_predicted.png")
    plt.savefig(p1, dpi=300)
    plt.close()

    # Plot 2: Residual Plot
    residuals = best_preds_df["actual"] - best_preds_df["predicted"]
    plt.figure(figsize=(8, 6))
    plt.scatter(best_preds_df["predicted"], residuals, alpha=0.7, color="crimson", edgecolors="k")
    plt.axhline(0, color="black", linestyle="--")
    plt.xlabel("Predicted Cotton Yield (kg/ha)")
    plt.ylabel("Residual (Actual - Predicted kg/ha)")
    plt.title(f"Residual Plot ({best_model_name})")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p2 = os.path.join(PLOTS_DIR, "residuals_plot.png")
    plt.savefig(p2, dpi=300)
    plt.close()

    # Plot 3: Year-wise Prediction Performance
    year_perf = best_preds_df.groupby("test_year").apply(
        lambda g: mean_absolute_error(g["actual"], g["predicted"]),
        include_groups=False
    ).reset_index(name="MAE")

    plt.figure(figsize=(10, 5))
    plt.plot(year_perf["test_year"], year_perf["MAE"], marker="o", color="navy", linewidth=2)
    plt.xlabel("Test Year")
    plt.ylabel("Out-of-Sample MAE (kg/ha)")
    plt.title(f"Year-wise Out-of-Sample MAE ({best_model_name} 2011–2024)")
    plt.xticks(year_perf["test_year"], rotation=45)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    p3 = os.path.join(PLOTS_DIR, "yearwise_performance.png")
    plt.savefig(p3, dpi=300)
    plt.close()

    # Plot 4: District-wise Prediction Performance
    dist_perf = best_preds_df.groupby("district").apply(
        lambda g: mean_absolute_error(g["actual"], g["predicted"]),
        include_groups=False
    ).reset_index(name="MAE").sort_values(by="MAE", ascending=True)

    plt.figure(figsize=(9, 5))
    plt.barh(dist_perf["district"], dist_perf["MAE"], color="darkgreen", edgecolor="black")
    plt.xlabel("Out-of-Sample MAE (kg/ha)")
    plt.ylabel("District")
    plt.title(f"District-wise Out-of-Sample MAE ({best_model_name})")
    plt.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    p4 = os.path.join(PLOTS_DIR, "districtwise_performance.png")
    plt.savefig(p4, dpi=300)
    plt.close()

    print(f"Generated and saved all 4 evaluation plots into: {PLOTS_DIR}")
    print("\nML Pipeline Execution Completed Successfully!")

if __name__ == "__main__":
    main()
