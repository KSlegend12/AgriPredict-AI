"""
Compute and save authoritative global SHAP explanations for the production GradientBoosting model.
Uses 1997-2023 development data to prevent leakage from the 2024 holdout.
"""

import os
import sys
import json
import joblib
import shap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = r"C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI"
sys.path.insert(0, PROJECT_ROOT)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "vidarbha_cotton_model_ready_1997_2024.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "backend", "ml", "artifacts", "final_model.pkl")
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "backend", "ml", "artifacts", "global_shap_importance.json")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "backend", "ml", "artifacts", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

from backend.ml.cotton_predictor import FEATURE_COLS, HUMAN_READABLE_NAMES

FEATURE_CATEGORIES = {
    "cotton_area_000ha": "Agricultural Sown Area",
    
    "previous_year_yield_kg_ha": "Historical Yield Trend",
    "previous_2year_yield_kg_ha": "Historical Yield Trend",
    "rolling_3yr_yield_mean_kg_ha": "Historical Yield Trend",
    
    "rainfall_annual_mm": "Meteorological / Rainfall",
    "rainy_days_annual": "Meteorological / Rainfall",
    "heavy_rain_days_annual": "Meteorological / Rainfall",
    "rainfall_max_1day_annual_mm": "Meteorological / Rainfall",
    "max_5day_rain_annual_mm": "Meteorological / Rainfall",
    "max_dry_spell_annual_days": "Meteorological / Rainfall",
    "rainfall_monsoon_mm": "Meteorological / Rainfall",
    "rainy_days_monsoon": "Meteorological / Rainfall",
    "heavy_rain_days_monsoon": "Meteorological / Rainfall",
    "rainfall_max_1day_monsoon_mm": "Meteorological / Rainfall",
    "max_5day_rain_monsoon_mm": "Meteorological / Rainfall",
    "max_dry_spell_monsoon_days": "Meteorological / Rainfall",
    "rainfall_kharif_mm": "Meteorological / Rainfall",
    "rainy_days_kharif": "Meteorological / Rainfall",
    "heavy_rain_days_kharif": "Meteorological / Rainfall",
    "rainfall_max_1day_kharif_mm": "Meteorological / Rainfall",
    "max_5day_rain_kharif_mm": "Meteorological / Rainfall",
    "max_dry_spell_kharif_days": "Meteorological / Rainfall",
    "rainfall_monsoon_mm_district_anomaly": "Meteorological / Rainfall",
    "rainfall_kharif_mm_district_anomaly": "Meteorological / Rainfall",
    
    "tmax_annual_mean_c": "Temperature & Extremes",
    "tmax_monsoon_mean_c": "Temperature & Extremes",
    "tmax_kharif_mean_c": "Temperature & Extremes",
    "tmax_max_c": "Temperature & Extremes",
    "tmax_hot_days_ge35_kharif": "Temperature & Extremes",
    "tmin_annual_mean_c": "Temperature & Extremes",
    "tmin_monsoon_mean_c": "Temperature & Extremes",
    "tmin_kharif_mean_c": "Temperature & Extremes",
    "tmin_min_c": "Temperature & Extremes",
    "tmax_kharif_mean_c_district_anomaly": "Temperature & Extremes",
    "tmin_kharif_mean_c_district_anomaly": "Temperature & Extremes",
    
    "district_Akola": "Geographic District Baseline",
    "district_Amravati": "Geographic District Baseline",
    "district_Buldhana": "Geographic District Baseline",
    "district_Nagpur": "Geographic District Baseline",
    "district_Wardha": "Geographic District Baseline",
    "district_Washim": "Geographic District Baseline",
    "district_Yavatmal": "Geographic District Baseline",
}

def main():
    print("Loading production model and data...")
    pipe = joblib.load(MODEL_PATH)
    prep = pipe.named_steps["preprocessor"]
    model = pipe.named_steps["model"]
    
    df = pd.read_csv(DATA_PATH)
    dev_df = df[df["year"] < 2024].copy()
    print(f"Using development dataset (1997-2023): {len(dev_df)} rows")
    
    X_dev = dev_df[FEATURE_COLS]
    X_trans = prep.transform(X_dev)
    
    # Feature names
    num_cols = prep.transformers_[0][2]
    cat_cols = prep.transformers_[1][2]
    ohe = prep.named_transformers_["cat"].named_steps["onehot"]
    ohe_names = list(ohe.get_feature_names_out(cat_cols))
    trans_feature_names = list(num_cols) + ohe_names
    
    print("Initializing SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_trans)
    base_value = float(explainer.expected_value)
    if isinstance(base_value, np.ndarray):
        base_value = float(base_value[0])
        
    print(f"SHAP values calculated. Base value: {base_value:.2f} kg/ha. Shape: {shap_values.shape}")
    
    # Global metrics per feature
    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
    mean_shap = np.mean(shap_values, axis=0)
    min_shap = np.min(shap_values, axis=0)
    max_shap = np.max(shap_values, axis=0)
    pos_freq = np.mean(shap_values > 0, axis=0) * 100
    
    features_summary = []
    total_mean_abs = float(np.sum(mean_abs_shap))
    
    for i, fname in enumerate(trans_feature_names):
        display_name = HUMAN_READABLE_NAMES.get(fname, fname.replace("_", " ").title())
        category = FEATURE_CATEGORIES.get(fname, "Other Agro-Climatic Factor")
        m_abs = float(mean_abs_shap[i])
        rel_imp = float((m_abs / total_mean_abs) * 100) if total_mean_abs > 0 else 0.0
        
        features_summary.append({
            "feature": fname,
            "display_name": display_name,
            "category": category,
            "mean_abs_shap_kg_ha": round(m_abs, 3),
            "mean_shap_kg_ha": round(float(mean_shap[i]), 3),
            "min_shap_kg_ha": round(float(min_shap[i]), 3),
            "max_shap_kg_ha": round(float(max_shap[i]), 3),
            "relative_importance_pct": round(rel_imp, 2),
            "positive_impact_frequency_pct": round(float(pos_freq[i]), 1),
        })
        
    features_summary.sort(key=lambda x: x["mean_abs_shap_kg_ha"], reverse=True)
    
    # Category level aggregation
    cat_importance = {}
    for f in features_summary:
        c = f["category"]
        cat_importance[c] = cat_importance.get(c, 0.0) + f["mean_abs_shap_kg_ha"]
        
    category_summary = [
        {"category": k, "mean_abs_shap_kg_ha": round(v, 2), "relative_importance_pct": round((v / total_mean_abs) * 100, 1)}
        for k, v in sorted(cat_importance.items(), key=lambda x: x[1], reverse=True)
    ]
    
    result = {
        "methodology": "SHAP (SHapley Additive exPlanations) TreeExplainer",
        "model_name": "GradientBoostingRegressor (Validated Production Pipeline)",
        "training_period": "1997-2023",
        "sample_count": len(dev_df),
        "base_value_kg_ha": round(base_value, 2),
        "total_features": len(features_summary),
        "category_summary": category_summary,
        "global_feature_importance": features_summary,
        "top_10_features": features_summary[:10],
    }
    
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Saved global SHAP JSON to {OUTPUT_JSON}")
    
    # Save bar chart visualization
    top15 = features_summary[:15]
    plt.figure(figsize=(10, 6))
    names = [f["display_name"] for f in reversed(top15)]
    vals = [f["mean_abs_shap_kg_ha"] for f in reversed(top15)]
    colors = ["#10b981" if "Yield" in f["category"] else "#3b82f6" if "Meteorological" in f["category"] else "#f59e0b" for f in reversed(top15)]
    
    plt.barh(range(len(names)), vals, color=colors, align="center")
    plt.yticks(range(len(names)), names, fontsize=9)
    plt.xlabel("Mean |SHAP Value| (Impact on Cotton Yield in kg/ha)", fontsize=10)
    plt.title("AgriPredict-AI: Top 15 Global Feature Importances (SHAP TreeExplainer)", fontsize=12, pad=12)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot_path = os.path.join(PLOTS_DIR, "global_shap_importance.png")
    plt.savefig(plot_path, dpi=180)
    plt.close()
    print(f"Saved global SHAP plot to {plot_path}")

if __name__ == "__main__":
    main()
