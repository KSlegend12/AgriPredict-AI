# AgriPredict-AI: Final Model Validation Report

**Generated:** 2026-09-17 20:50  
**Dataset:** vidarbha_cotton_model_ready_1997_2024.csv  
**Target:** yield_target_kg_ha (cotton yield in kg/ha)  
**Crop:** Cotton (Gossypium hirsutum)  
**Districts:** Akola, Amravati, Buldhana, Nagpur, Wardha, Washim, Yavatmal  
**Development set:** 1997-2023 (187 rows)  
**Holdout set:** 2024 (7 rows) -- evaluated EXACTLY ONCE  

---

## Methodological Integrity

**2024 holdout integrity: MAINTAINED.**

- 2024 was used for **nothing** during model selection, feature selection, or hyperparameter tuning.
- 2024 was evaluated **exactly once** after final model training.
- Model selection folds: expanding-window **2011-2023 only** (13 folds).
- Lag feature audit: No contamination issues detected.

---

## Model Selection Summary (2011-2023 Folds Only)

| Model | Mean MAE | Std MAE | Mean RMSE | Mean R2 | Mean MAPE |
|---|---|---|---|---|---|
| GradientBoosting | 106.18 | 56.64 | 126.65 | -1.5769 | 38.16% |
| RandomForest | 107.16 | 63.11 | 127.07 | -1.7283 | 39.10% |
| HistGradientBoosting | 109.06 | 66.26 | 130.58 | -1.5076 | 38.27% |
| Ridge | 109.96 | 58.58 | 128.12 | -1.8803 | 41.70% |
| ExtraTrees | 114.69 | 68.00 | 137.32 | -2.7252 | 41.69% |
| Baseline_PrevYear | 121.82 | 78.78 | 147.22 | -4.2147 | 45.30% |
| Baseline_HistMean | 137.01 | 92.49 | 159.47 | -2.4177 | 39.31% |

**Selected model:** GradientBoosting  
**Selection criterion:** Lowest Mean MAE on 2011-2023 expanding-window folds.

| Metric | Value |
|---|---|
| Mean MAE (2011-2023) | 106.18 kg/ha |
| Std MAE (fold stability) | 56.64 kg/ha |
| Mean RMSE | 126.65 kg/ha |
| Mean R2 | -1.5769 |
| Mean MAPE | 38.16% |
| Selected hyperparams | {'n_estimators': 100, 'learning_rate': 0.05, 'max_depth': 3} |
| Beats PrevYear baseline | YES |
| Beats HistMean baseline | YES |

---

## Lag Feature Sensitivity (2011-2023 Folds Only)

| Feature Config | Mean MAE | Mean RMSE | Mean R2 | Mean MAPE |
|---|---|---|---|---|
| All_Features | 106.18 | 126.65 | -1.5769 | 38.16% |
| Weather+Area_Only | 118.11 | 142.57 | -2.0113 | 34.68% |
| Lag+District_Only | 124.43 | 151.36 | -3.5464 | 44.56% |
| Weather+Lag | 107.38 | 127.31 | -1.6219 | 38.56% |

---

## Final Model Training

- **Model:** GradientBoosting
- **Training data:** 1997-2023 (187 rows)
- **2024 excluded from training:** CONFIRMED

---

## 2024 Holdout Results (Evaluated Once -- No Retraining After)

> These are the **definitive, final results**.
> No retraining or tuning was performed after 2024 evaluation.

| Metric | Value |
|---|---|
| MAE | 230.75 kg/ha |
| RMSE | 321.45 kg/ha |
| R2 | -0.6360 |
| MAPE | 41.69% |
| Baseline PrevYear MAE | 189.86 kg/ha |
| Baseline HistMean MAE | 281.18 kg/ha |
| Beats PrevYear | NO |
| Beats HistMean | YES |

### 2024 Per-District Results

| District | Actual (kg/ha) | Predicted (kg/ha) | Error (kg/ha) | MAPE |
|---|---|---|---|---|
| Akola | 261 | 396 | -135 | 51.5% |
| Amravati | 572 | 411 | 161 | 28.1% |
| Buldhana | 281 | 439 | -158 | 56.4% |
| Nagpur | 390 | 509 | -119 | 30.4% |
| Wardha | 462 | 344 | 118 | 25.5% |
| Washim | 550 | 403 | 147 | 26.7% |
| Yavatmal | 1063 | 285 | 778 | 73.1% |

---

## Diagnostic Notes

### On R2 Interpretation
R2 measures variance explained relative to predicting the mean. A negative R2 means
the model explains less variance than a mean predictor in that evaluation window.
This does not invalidate the model -- the MAE comparison to baselines is the more
informative measure for this dataset (194 rows, 7 districts, 28 years).

### On MAE Interpretation
The model's rolling-origin validation mean MAE was 106.18 kg/ha
across the 2011-2023 selection folds. This is NOT a confidence interval.

### On Yavatmal 2024
Yavatmal experienced an exceptional yield recovery in 2024 (~2.7x vs its 2023 value).
Lag features anchored predictions to historical averages and could not anticipate this
structural break. This is a known limitation of autoregressive prediction features.

---

## SHAP / XAI Status

SHAP TreeExplainer: WORKING -- verified on 2024 holdout samples.  
Base value (expected output): 230.73 kg/ha

---

## Artifacts Saved

| Artifact | Path |
|---|---|
| Final model pipeline | artifacts/final_model.pkl |
| Preprocessor | artifacts/preprocessor.pkl |
| Feature schema | artifacts/feature_schema.json |
| Model metadata | artifacts/model_metadata.json |
| 2024 holdout results | evaluation/final/actual_vs_predicted_2024.csv |
| District results | evaluation/final/final_2024_district_results.csv |
| Model comparison | evaluation/final/model_comparison_2011_2023.csv |
| Selected config | evaluation/final/selected_model_config.json |
| Lag sensitivity | evaluation/final/lag_sensitivity_2011_2023.csv |
| SHAP importances | evaluation/final/shap_feature_importance.csv |
| 2024 holdout plot | evaluation/final/plots/actual_vs_predicted_2024.png |
| Selection folds plot | evaluation/final/plots/selection_actual_vs_predicted.png |
