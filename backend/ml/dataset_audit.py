import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

# ML Models
from sklearn.linear_model import Ridge
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor
)
import xgboost as xgb

# ---------------------------------------------------------
# CONSTANTS & PATHS
# ---------------------------------------------------------
PROJECT_ROOT = r"C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI"
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "vidarbha_cotton_model_ready_1997_2024.csv")
BACKEND_ML_DIR = os.path.join(PROJECT_ROOT, "backend", "ml")
ARTIFACTS_DIR = os.path.join(BACKEND_ML_DIR, "artifacts")
PLOTS_DIR = os.path.join(BACKEND_ML_DIR, "evaluation", "plots")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. DATASET AUDIT
# ---------------------------------------------------------
def run_dataset_audit(df):
    print("=" * 80)
    print("STEP 1 — DATASET AUDIT REPORT")
    print("=" * 80)
    
    n_rows, n_cols = df.shape
    print(f"Number of rows: {n_rows}")
    print(f"Number of columns: {n_cols}")
    
    # Missing values
    missing_series = df.isnull().sum()
    cols_with_missing = missing_series[missing_series > 0]
    print(f"\nMissing values per column:")
    if len(cols_with_missing) == 0:
        print("  None (0 missing values across all columns)")
    else:
        for col, count in cols_with_missing.items():
            pct = (count / n_rows) * 100
            print(f"  - {col}: {count} missing ({pct:.2f}%)")
            
    # Duplicate rows
    dup_rows = df.duplicated().sum()
    print(f"\nDuplicate rows: {dup_rows}")
    
    # District + Year uniqueness
    dup_dist_year = df.duplicated(subset=['district', 'year']).sum()
    print(f"Duplicate (district, year) combinations: {dup_dist_year}")
    
    # Unique districts & years
    districts = sorted(df['district'].unique().tolist())
    years = sorted(df['year'].unique().tolist())
    print(f"\nUnique districts ({len(districts)}): {districts}")
    print(f"Year range: {min(years)} to {max(years)} ({len(years)} consecutive years)")
    
    # District-year completeness check
    expected_rows = len(districts) * len(years)
    print(f"Expected district-year combinations ({len(districts)} x {len(years)}): {expected_rows}")
    print(f"Actual rows: {n_rows}")
    
    # Target availability check
    target_col = 'yield_target_kg_ha'
    target_nulls = df[target_col].isnull().sum()
    print(f"\nTarget column ('{target_col}') missing values: {target_nulls}")
    
    # Target statistics
    target_stats = df[target_col].describe()
    print(f"\nTarget Statistics ({target_col} in kg/ha):")
    print(f"  Mean:   {target_stats['mean']:.2f}")
    print(f"  Std:    {target_stats['std']:.2f}")
    print(f"  Min:    {target_stats['min']:.2f}")
    print(f"  25%:    {target_stats['25%']:.2f}")
    print(f"  50%:    {target_stats['50%']:.2f}")
    print(f"  75%:    {target_stats['75%']:.2f}")
    print(f"  Max:    {target_stats['max']:.2f}")
    print(f"  Skewness: {df[target_col].skew():.2f}")
    
    # Categorical vs Numerical
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    print(f"\nCategorical columns ({len(cat_cols)}): {cat_cols}")
    print(f"Numerical columns ({len(num_cols)}): {len(num_cols)} columns")
    
    validation_passed = (dup_dist_year == 0) and (target_nulls == 0) and (n_rows == 194)
    print(f"\nDataset Validation Status: {'PASSED' if validation_passed else 'FAILED'}")
    print("=" * 80 + "\n")
    return validation_passed

# ---------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------
if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    audit_passed = run_dataset_audit(df)
    if not audit_passed:
        sys.exit("Dataset failed audit checks!")
