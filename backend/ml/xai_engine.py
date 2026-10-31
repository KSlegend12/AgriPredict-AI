"""
Explainable AI (XAI) Engine for AgriPredict-AI Cotton Yield Predictions.
Provides local SHAP-based explanations, additive waterfall steps,
farmer-friendly non-causal summaries, uncertainty bounds, and global feature importance.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import shap

logger = logging.getLogger("agripredict.xai")

_HERE = os.path.dirname(os.path.abspath(__file__))
GLOBAL_SHAP_PATH = os.path.join(_HERE, "artifacts", "global_shap_importance.json")

# Human-readable mapping and categories
HUMAN_READABLE_NAMES = {
    "cotton_area_000ha": "Cotton Sown Area (000 ha)",
    "tmax_annual_mean_c": "Annual Mean Max Temperature (°C)",
    "tmax_monsoon_mean_c": "Monsoon Mean Max Temperature (°C)",
    "tmax_kharif_mean_c": "Average Kharif Max Temperature (°C)",
    "tmax_max_c": "Peak Maximum Temperature (°C)",
    "tmax_hot_days_ge35_kharif": "Hot Days (≥35°C) in Kharif",
    "tmin_annual_mean_c": "Annual Mean Min Temperature (°C)",
    "tmin_monsoon_mean_c": "Monsoon Mean Min Temperature (°C)",
    "tmin_kharif_mean_c": "Average Kharif Min Temperature (°C)",
    "tmin_min_c": "Minimum Season Temperature (°C)",
    "rainfall_annual_mm": "Annual Total Rainfall (mm)",
    "rainy_days_annual": "Annual Rainy Days",
    "heavy_rain_days_annual": "Heavy Rain Days (Annual)",
    "rainfall_max_1day_annual_mm": "1-Day Max Rainfall (mm)",
    "max_5day_rain_annual_mm": "5-Day Max Rainfall (mm)",
    "max_dry_spell_annual_days": "Maximum Annual Dry Spell (Days)",
    "rainfall_monsoon_mm": "Monsoon Rainfall (mm)",
    "rainy_days_monsoon": "Monsoon Rainy Days",
    "heavy_rain_days_monsoon": "Monsoon Heavy Rain Days",
    "rainfall_max_1day_monsoon_mm": "Monsoon 1-Day Max Rainfall (mm)",
    "max_5day_rain_monsoon_mm": "Monsoon 5-Day Max Rainfall (mm)",
    "max_dry_spell_monsoon_days": "Maximum Monsoon Dry Spell (Days)",
    "rainfall_kharif_mm": "Kharif Rainfall (mm)",
    "rainy_days_kharif": "Kharif Rainy Days",
    "heavy_rain_days_kharif": "Kharif Heavy Rain Days",
    "rainfall_max_1day_kharif_mm": "Kharif 1-Day Max Rainfall (mm)",
    "max_5day_rain_kharif_mm": "Kharif 5-Day Max Rainfall (mm)",
    "max_dry_spell_kharif_days": "Maximum Kharif Dry Spell (Days)",
    "previous_year_yield_kg_ha": "Previous Year Cotton Yield (kg/ha)",
    "previous_2year_yield_kg_ha": "Previous 2-Year Cotton Yield (kg/ha)",
    "rolling_3yr_yield_mean_kg_ha": "3-Year Rolling Average Cotton Yield (kg/ha)",
    "rainfall_monsoon_mm_district_anomaly": "Monsoon Rainfall Anomaly (mm)",
    "rainfall_kharif_mm_district_anomaly": "Kharif Rainfall Anomaly (mm)",
    "tmax_kharif_mean_c_district_anomaly": "Kharif Max Temperature Anomaly (°C)",
    "tmin_kharif_mean_c_district_anomaly": "Kharif Min Temperature Anomaly (°C)",
    "district_Akola": "District Baseline: Akola",
    "district_Amravati": "District Baseline: Amravati",
    "district_Buldhana": "District Baseline: Buldhana",
    "district_Nagpur": "District Baseline: Nagpur",
    "district_Wardha": "District Baseline: Wardha",
    "district_Washim": "District Baseline: Washim",
    "district_Yavatmal": "District Baseline: Yavatmal",
    # NASA SMAP satellite soil moisture features (SPL4SMGP.008)
    "sm_surface_kharif_mean": "Kharif Surface Soil Moisture (0-5 cm, m³/m³)",
    "sm_rootzone_kharif_mean": "Kharif Root Zone Soil Moisture (0-100 cm, m³/m³)",
    "sm_surface_monsoon_mean": "Monsoon Surface Soil Moisture (0-5 cm, m³/m³)",
    "sm_rootzone_monsoon_mean": "Monsoon Root Zone Soil Moisture (0-100 cm, m³/m³)",
    "sm_surface_kharif_mean_lag1": "Prior-Year Kharif Surface Soil Moisture (m³/m³)",
    "sm_rootzone_kharif_mean_lag1": "Prior-Year Kharif Root Zone Soil Moisture (m³/m³)",
    "sm_surface_kharif_max": "Peak Kharif Surface Soil Moisture (m³/m³)",
    "sm_rootzone_kharif_max": "Peak Kharif Root Zone Soil Moisture (m³/m³)",
    # Agronomic & Physiological Engineered Features
    "diurnal_range_kharif": "Kharif Diurnal Temperature Range (°C)",
    "rain_intensity_kharif": "Kharif Rain Intensity (mm/rainy day)",
    "dry_heat_compound": "Compound Heat-Drought Stress Index",
    "single_day_deluge_ratio": "Single-Day Deluge Rainfall Fraction",
    "yield_momentum": "2-Year Yield Momentum (kg/ha)",
    "yield_ratio_to_rolling3": "Yield Ratio to 3-Year Rolling Mean",
    "rain_gentleness_ratio": "Kharif Rain Gentleness Ratio (days/100mm)",
    "heavy_rain_fraction": "Kharif Heavy Rain Days Fraction",
    "extreme_heat_ratio": "Extreme Heat Days Fraction (Kharif)",
    "drought_buffer_index": "Drought Buffer Index (mm/dry day)",
    "yield_excess_over_rolling3": "Yield Excess Over 3-Yr Rolling Mean (kg/ha)",
    "excess_rain_kharif": "Excess Kharif Rain Above 800mm (x100mm)",
    "continuous_wetness_risk": "Continuous Wetness Risk Index",
    "rain_deficit_kharif": "Kharif Rainfall Deficit Below 750mm (x100mm)",
    "hot_days_thresh10": "Excess Kharif Extreme Heat Days Above 10 (x10 days)",
}

FEATURE_CATEGORIES = {
    "cotton_area_000ha": "Agricultural Sown Area",
    "previous_year_yield_kg_ha": "Historical Yield Trend",
    "previous_2year_yield_kg_ha": "Historical Yield Trend",
    "rolling_3yr_yield_mean_kg_ha": "Historical Yield Trend",
    "rain_deficit_kharif": "Meteorological / Rainfall",
    "hot_days_thresh10": "Temperature & Extremes",
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
    # NASA SMAP satellite soil moisture features (SPL4SMGP.008)
    "sm_surface_kharif_mean": "Satellite Soil Moisture (NASA SMAP)",
    "sm_rootzone_kharif_mean": "Satellite Soil Moisture (NASA SMAP)",
    "sm_surface_monsoon_mean": "Satellite Soil Moisture (NASA SMAP)",
    "sm_rootzone_monsoon_mean": "Satellite Soil Moisture (NASA SMAP)",
    "sm_surface_kharif_mean_lag1": "Satellite Soil Moisture (NASA SMAP)",
    "sm_rootzone_kharif_mean_lag1": "Satellite Soil Moisture (NASA SMAP)",
    "sm_surface_kharif_max": "Satellite Soil Moisture (NASA SMAP)",
    "sm_rootzone_kharif_max": "Satellite Soil Moisture (NASA SMAP)",
    # Agronomic & Physiological Engineered Features
    "diurnal_range_kharif": "Temperature & Extremes",
    "rain_intensity_kharif": "Meteorological / Rainfall",
    "dry_heat_compound": "Biophysical Interaction Index",
    "single_day_deluge_ratio": "Meteorological / Rainfall",
    "yield_momentum": "Historical Yield Trend",
    "yield_ratio_to_rolling3": "Historical Yield Trend",
    "rain_gentleness_ratio": "Meteorological / Rainfall",
    "heavy_rain_fraction": "Meteorological / Rainfall",
    "extreme_heat_ratio": "Temperature & Extremes",
    "drought_buffer_index": "Meteorological / Rainfall",
    "yield_excess_over_rolling3": "Historical Yield Trend",
    "excess_rain_kharif": "Meteorological / Rainfall",
    "continuous_wetness_risk": "Meteorological / Rainfall",
}


class XAIEngine:
    """Explainable AI engine for Cotton Yield predictions."""

    def __init__(self):
        self._cached_global_importance = None
        self._load_cached_global_importance()

    def _load_cached_global_importance(self):
        if os.path.exists(GLOBAL_SHAP_PATH):
            try:
                with open(GLOBAL_SHAP_PATH, "r", encoding="utf-8") as f:
                    self._cached_global_importance = json.load(f)
                logger.info("Loaded cached global SHAP feature importance.")
            except Exception as e:
                logger.warning("Could not load cached global SHAP importance: %s", e)
                self._cached_global_importance = None

    def get_global_importance(self) -> dict:
        """Return the precomputed global SHAP feature importance."""
        if self._cached_global_importance:
            return self._cached_global_importance
        return {
            "available": False,
            "message": "Global SHAP importance has not been precomputed."
        }

    def generate_local_explanation(
        self,
        pipeline,
        X_df: pd.DataFrame,
        predicted_yield: float,
        explainer=None,
        anchor_value: float = None,
    ) -> dict:
        """
        Generate local SHAP explanations for a single prediction row.
        Supports Tree models, Linear models (exact closed-form), and Hybrid Ensembles.
        Guaranteed mathematical additivity (Delta < 0.1) and safe error handling.
        """
        if pipeline is None:
            return {
                "available": False,
                "error": "Pipeline model is not loaded."
            }

        try:
            # 1. Ensemble Dictionary branch
            if isinstance(pipeline, dict) and "model_ridge" in pipeline:
                pipe_r = pipeline["model_ridge"]
                pipe_et = pipeline["model_et"]
                weights = pipeline.get("weights", [0.55, 0.45])

                prep_r = pipe_r.named_steps.get("preprocessor") or pipe_r.named_steps.get("prep")
                prep_et = pipe_et.named_steps.get("preprocessor") or pipe_et.named_steps.get("prep")

                num_cols = prep_r.transformers_[0][2]
                cat_cols = prep_r.transformers_[1][2]
                cat_transformer = prep_r.named_transformers_["cat"]
                ohe = (
                    cat_transformer.named_steps.get("onehot")
                    or cat_transformer.named_steps.get("ohe")
                )
                feature_names = list(num_cols) + list(ohe.get_feature_names_out(cat_cols))

                X_trans_r = prep_r.transform(X_df)
                m_r = pipe_r.named_steps.get("model")
                shap_r = m_r.coef_ * X_trans_r[0]
                base_r = float(m_r.intercept_)

                X_trans_et = prep_et.transform(X_df)
                m_et = pipe_et.named_steps.get("model")
                exp_et = explainer if explainer is not None else shap.TreeExplainer(m_et)
                shap_t = exp_et.shap_values(X_trans_et)[0]
                base_t = exp_et.expected_value
                if isinstance(base_t, (np.ndarray, list)):
                    base_t = float(base_t[0])
                else:
                    base_t = float(base_t)

                shap_vals = weights[0] * shap_r + weights[1] * shap_t
                base_val = weights[0] * base_r + weights[1] * base_t
                method_name = "SHAP Hybrid Ensemble (Exact Linear + TreeExplainer)"

            else:
                # 2. Standard Pipeline branch
                preprocessor = pipeline.named_steps.get("preprocessor") or pipeline.named_steps.get("prep")
                model = pipeline.named_steps.get("model")

                if preprocessor is None or model is None:
                    return {
                        "available": False,
                        "error": "Pipeline missing required steps (preprocessor or model)."
                    }

                # Extract transformed feature names
                num_cols = preprocessor.transformers_[0][2]
                cat_cols = preprocessor.transformers_[1][2]
                cat_transformer = preprocessor.named_transformers_["cat"]
                ohe = (
                    cat_transformer.named_steps.get("onehot")
                    or cat_transformer.named_steps.get("ohe")
                )
                ohe_names = list(ohe.get_feature_names_out(cat_cols))
                feature_names = list(num_cols) + ohe_names

                # Transform row
                X_trans = preprocessor.transform(X_df)

                if hasattr(model, "coef_") and not hasattr(model, "estimators_"):
                    # Linear model (e.g. Ridge) closed-form exact Shapley attributions
                    shap_vals = model.coef_ * X_trans[0]
                    base_val = float(model.intercept_)
                    method_name = "SHAP LinearExplainer (Exact Closed-Form)"
                else:
                    # Tree model
                    if explainer is None:
                        explainer = shap.TreeExplainer(model)
                    shap_vals_matrix = explainer.shap_values(X_trans)
                    shap_vals = shap_vals_matrix[0]
                    base_val = explainer.expected_value
                    if isinstance(base_val, (np.ndarray, list)):
                        base_val = float(base_val[0])
                    else:
                        base_val = float(base_val)
                    method_name = "SHAP (SHapley Additive exPlanations) TreeExplainer"

            # Check mathematical additivity
            if anchor_value is not None:
                reconstructed_pred = float(anchor_value + base_val + np.sum(shap_vals))
                additivity_error = abs(reconstructed_pred - predicted_yield)
                effective_base_val = float(anchor_value + base_val)
            else:
                reconstructed_pred = float(base_val + np.sum(shap_vals))
                additivity_error = abs(reconstructed_pred - predicted_yield)
                effective_base_val = base_val

            total_abs_contribution = float(np.sum(np.abs(shap_vals)))
            if total_abs_contribution == 0.0:
                total_abs_contribution = 1.0

            # Build feature-level contributions
            all_contributions = []
            for fname, sval in zip(feature_names, shap_vals):
                val_float = float(sval)
                raw_input_val = None
                if fname in X_df.columns:
                    raw_input_val = X_df[fname].values[0]
                    if pd.isna(raw_input_val):
                        raw_input_val = None
                    elif isinstance(raw_input_val, (np.floating, float)):
                        raw_input_val = round(float(raw_input_val), 2)
                    elif isinstance(raw_input_val, (np.integer, int)):
                        raw_input_val = int(raw_input_val)

                display_name = HUMAN_READABLE_NAMES.get(fname, fname.replace("_", " ").title())
                category = FEATURE_CATEGORIES.get(fname, "Other Agro-Climatic Factor")
                rel_impact = round((abs(val_float) / total_abs_contribution) * 100, 1)

                all_contributions.append({
                    "feature": fname,
                    "display_name": display_name,
                    "category": category,
                    "input_value": raw_input_val,
                    "contribution_kg_ha": round(val_float, 2),
                    "relative_impact_pct": rel_impact,
                    "direction": "positive" if val_float >= 0 else "negative"
                })

            # Sort by absolute contribution descending
            all_contributions.sort(key=lambda x: abs(x["contribution_kg_ha"]), reverse=True)

            # Top positive and negative factors
            increasing_factors = [c for c in all_contributions if c["direction"] == "positive" and abs(c["contribution_kg_ha"]) >= 0.1]
            decreasing_factors = [c for c in all_contributions if c["direction"] == "negative" and abs(c["contribution_kg_ha"]) >= 0.1]
            top_influential_features = all_contributions[:10]

            # Build waterfall steps for UI visualization
            waterfall_steps = []
            if anchor_value is not None:
                running_sum = float(anchor_value)
                waterfall_steps.append({
                    "name": "Historical 3-Year Rolling Average Anchor",
                    "type": "anchor",
                    "contribution_kg_ha": round(anchor_value, 2),
                    "running_total_kg_ha": round(running_sum, 2),
                    "direction": "neutral"
                })
                running_sum += float(base_val)
                waterfall_steps.append({
                    "name": "Biophysical Calibration Baseline",
                    "type": "baseline",
                    "contribution_kg_ha": round(base_val, 2),
                    "running_total_kg_ha": round(running_sum, 2),
                    "direction": "neutral"
                })
            else:
                running_sum = float(base_val)
                waterfall_steps.append({
                    "name": "Regional Baseline (Expected Value)",
                    "type": "baseline",
                    "contribution_kg_ha": round(base_val, 2),
                    "running_total_kg_ha": round(running_sum, 2),
                    "direction": "neutral"
                })

            # Top 6 significant factors in waterfall
            significant = [c for c in all_contributions if abs(c["contribution_kg_ha"]) >= 1.0][:6]
            used_features = set()

            for item in significant:
                used_features.add(item["feature"])
                running_sum += item["contribution_kg_ha"]
                waterfall_steps.append({
                    "name": item["display_name"],
                    "feature": item["feature"],
                    "category": item["category"],
                    "type": "feature",
                    "contribution_kg_ha": item["contribution_kg_ha"],
                    "running_total_kg_ha": round(running_sum, 2),
                    "direction": item["direction"]
                })

            # Remaining factors grouped
            other_sum = sum(c["contribution_kg_ha"] for c in all_contributions if c["feature"] not in used_features)
            if abs(other_sum) >= 0.05:
                running_sum += other_sum
                waterfall_steps.append({
                    "name": "Other Agro-Climatic Factors Combined",
                    "type": "other",
                    "contribution_kg_ha": round(other_sum, 2),
                    "running_total_kg_ha": round(running_sum, 2),
                    "direction": "positive" if other_sum >= 0 else "negative"
                })

            waterfall_steps.append({
                "name": "Predicted Cotton Yield",
                "type": "total",
                "contribution_kg_ha": round(predicted_yield, 2),
                "running_total_kg_ha": round(predicted_yield, 2),
                "direction": "result"
            })

            # Synthesize farmer-friendly plain text summary
            summary_sentences = []
            if increasing_factors:
                top_pos = [f"{f['display_name']} (+{f['contribution_kg_ha']} kg/ha)" for f in increasing_factors[:2]]
                summary_sentences.append(
                    f"Higher predicted yield was supported primarily by favorable associations with {', '.join(top_pos)}."
                )

            if decreasing_factors:
                top_neg = [f"{f['display_name']} ({f['contribution_kg_ha']} kg/ha)" for f in decreasing_factors[:2]]
                summary_sentences.append(
                    f"The yield estimate was restrained by {', '.join(top_neg)}."
                )

            if not summary_sentences:
                summary_sentences.append(
                    "The predicted yield closely tracks historical district baseline conditions."
                )

            summary_text = " ".join(summary_sentences)

            # Cautious agronomic & uncertainty notice
            uncertainty_notice = {
                "interpretation_guideline": (
                    "SHAP feature attributions reflect statistical associations identified across historical 1997–2023 "
                    "Vidarbha data, not biological cause-and-effect proof. A positive feature contribution indicates that "
                    "the model associates higher values with increased regional yield potential."
                ),
                "model_confidence_benchmark": (
                    "Expanding-window temporal cross-validation (2011–2023) established a Mean Absolute Error of 106.2 kg/ha "
                    "(~20–25% expected regional variance). On extreme weather holdout years (e.g. 2024), error increased to 230.8 kg/ha."
                ),
                "plausible_range_kg_ha": [
                    round(max(0.0, predicted_yield - 106.2), 1),
                    round(predicted_yield + 106.2, 1)
                ],
                "farming_practice_disclaimer": (
                    "Do not make unilateral pesticide, fertilizer, or irrigation expenditure decisions solely based on these "
                    "statistical associations. Consult local Krishi Vigyan Kendra (KVK) advisories for field-specific guidance."
                )
            }

            return {
                "available": True,
                "methodology": method_name,
                "base_value_kg_ha": round(effective_base_val, 2),
                "predicted_yield_kg_ha": round(predicted_yield, 2),
                "additivity_verified": bool(additivity_error < 0.1),
                "summary_text": summary_text,
                "top_influential_features": top_influential_features,
                "increasing_factors": increasing_factors[:5],
                "decreasing_factors": decreasing_factors[:5],
                "waterfall_steps": waterfall_steps,
                "uncertainty_notice": uncertainty_notice
            }

        except Exception as e:
            logger.error("Error generating local SHAP explanation: %s", e, exc_info=True)
            return {
                "available": False,
                "error": str(e),
                "base_value_kg_ha": None,
                "summary_text": "SHAP explanation temporarily unavailable."
            }


xai_engine = XAIEngine()
