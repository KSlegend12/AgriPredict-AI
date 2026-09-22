Get-Content README.md# AgriPredict-AI � Project Status

**Last Updated:** 2026-09-17
**Status:** Validation complete. Servers startable. No further training required.

---

## 1. Authoritative Dataset

| Item | Value |
|---|---|
| Filename | `vidarbha_cotton_model_ready_1997_2024.csv` |
| Full path | `backend/data/vidarbha_cotton_model_ready_1997_2024.csv` |
| Dimensions | 194 rows x 43 columns |
| Do NOT | Modify, replace, re-download, or generate synthetic data for this file |

---

## 2. Dataset Details

### Target Column
```
yield_target_kg_ha
```
Unit: kg/ha (kilograms per hectare of cotton yield).

### 7 Districts (Vidarbha, Maharashtra)
1. Akola
2. Amravati
3. Buldhana
4. Nagpur
5. Wardha
6. Washim
7. Yavatmal

### Year Range
- Full dataset: 1997-2024 (28 years x 7 districts = 194 usable rows)
- **Training set (development):** 1997-2023 (187 rows)
- **Final holdout:** 2024 (7 rows, one per district)

---

## 3. Feature Schema

**Total features: 36** (35 numerical + 1 categorical)

### Categorical (1)
- `district`

### Numerical (35)
```
cotton_area_000ha
tmax_annual_mean_c, tmax_monsoon_mean_c, tmax_kharif_mean_c
tmax_max_c, tmax_hot_days_ge35_kharif
tmin_annual_mean_c, tmin_monsoon_mean_c, tmin_kharif_mean_c, tmin_min_c
rainfall_annual_mm, rainy_days_annual, heavy_rain_days_annual
rainfall_max_1day_annual_mm, max_5day_rain_annual_mm, max_dry_spell_annual_days
rainfall_monsoon_mm, rainy_days_monsoon, heavy_rain_days_monsoon
rainfall_max_1day_monsoon_mm, max_5day_rain_monsoon_mm, max_dry_spell_monsoon_days
rainfall_kharif_mm, rainy_days_kharif, heavy_rain_days_kharif
rainfall_max_1day_kharif_mm, max_5day_rain_kharif_mm, max_dry_spell_kharif_days
previous_year_yield_kg_ha       (lag t-1)
previous_2year_yield_kg_ha      (lag t-2)
rolling_3yr_yield_mean_kg_ha    (rolling mean of lag t-1 over 3 years)
rainfall_monsoon_mm_district_anomaly
rainfall_kharif_mm_district_anomaly
tmax_kharif_mean_c_district_anomaly
tmin_kharif_mean_c_district_anomaly
```

### Columns Excluded from Training
```
yield_target_kg_ha   (this IS the target)
year                 (used for temporal splitting only, not a predictor)
target_source_detail, target_review_flag, target_note
weather_temp_extraction, weather_rain_extraction
```

---

## 4. Lag Feature Contamination Audit

**Result: CLEAN. No contamination detected.**

All 3 lag columns verified per district against expected temporal shifts:
- `previous_year_yield_kg_ha` = `yield_target_kg_ha.shift(1)` per district ?
- `previous_2year_yield_kg_ha` = `yield_target_kg_ha.shift(2)` per district ?
- `rolling_3yr_yield_mean_kg_ha` = rolling(3).mean() of shift(1) per district ?

Current-year `yield_target_kg_ha` does NOT appear in any training feature.

---

## 5. Validation Methodology

**Type:** Expanding-window temporal cross-validation (no shuffling, no k-fold)
**Selection folds (test years):** 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
**Number of folds:** 13
**Protocol:** In each fold, train on all rows where year < test_year, predict rows where year == test_year.

**2024 holdout integrity:**
- 2024 was NEVER used for model selection, feature selection, or hyperparameter tuning.
- 2024 was evaluated EXACTLY ONCE after final model training.
- No retraining was performed after 2024 results were seen.

---

## 6. Candidate Model Comparison (2011-2023 Folds Only)

Selection criterion: Lowest Mean MAE across 13 expanding-window folds.
**Note: 2024 was NOT used in this comparison.**

| Rank | Model | Mean MAE | Std MAE | Mean RMSE | Std RMSE | Mean R2 | Mean MAPE |
|---|---|---|---|---|---|---|---|
| 1 SELECTED | GradientBoosting | 106.18 | 56.64 | 126.65 | 61.81 | -1.5769 | 38.16% |
| 2 | RandomForest | 107.16 | 63.11 | 127.07 | 65.93 | -1.7283 | 39.10% |
| 3 | HistGradientBoosting | 109.06 | 66.26 | 130.58 | 70.47 | -1.5076 | 38.27% |
| 4 | Ridge | 109.96 | 58.58 | 128.12 | 63.14 | -1.8803 | 41.70% |
| 5 | ExtraTrees | 114.69 | 68.00 | 137.32 | 70.60 | -2.7252 | 41.69% |
| � | Baseline: PrevYear | 121.82 | 78.78 | 147.22 | 83.30 | -4.2147 | 45.30% |
| � | Baseline: HistMean | 137.01 | 92.49 | 159.47 | 97.56 | -2.4177 | 39.31% |

---

## 7. Selected Model and Hyperparameters

**Model class:** `sklearn.ensemble.GradientBoostingRegressor`

**Exact hyperparameters:**
```json
{
  "n_estimators": 100,
  "learning_rate": 0.05,
  "max_depth": 3,
  "random_state": 42
}
```

**Preprocessing pipeline (sklearn Pipeline):**
1. `ColumnTransformer`:
   - Numerical: `SimpleImputer(strategy='median')` (no scaling � tree-based model)
   - Categorical: `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`
2. `GradientBoostingRegressor` (params above)

Beats Previous-Year baseline on 2011-2023 folds: YES (106.18 < 121.82)
Beats Historical-Mean baseline on 2011-2023 folds: YES (106.18 < 137.01)

---

## 8. Hyperparameter Tuning Results (2011-2023 Folds Only)

| Parameters | Mean MAE |
|---|---|
| n_estimators=100, lr=0.05, max_depth=3 **SELECTED** | 106.18 |
| n_estimators=200, lr=0.05, max_depth=3 | 107.64 |
| n_estimators=200, lr=0.03, max_depth=3 | 107.98 |
| n_estimators=150, lr=0.05, max_depth=4 | 112.45 |

Default parameters were already optimal. No improvement from larger/different configs.

---

## 9. Lag Feature Sensitivity Experiment (2011-2023 Folds Only)

| Feature Configuration | Mean MAE | Mean RMSE | Mean R2 | Mean MAPE |
|---|---|---|---|---|
| All Features (selected) | 106.18 | 126.65 | -1.5769 | 38.16% |
| Weather + Lag | 107.38 | 127.31 | -1.6219 | 38.56% |
| Weather + Area Only (no lag) | 118.11 | 142.57 | -2.0113 | 34.68% |
| Lag + District Only | 124.43 | 151.36 | -3.5464 | 44.56% |

Lag features improve prediction. Weather adds incremental value beyond lag alone.
All features together yields the lowest MAE.

---

## 10. Final Model Training

- Model: GradientBoosting (hyperparameters as above)
- Training data: 1997-2023 (187 rows)
- 2024 excluded from training: CONFIRMED
- Preprocessor fit on 1997-2023 training data only

---

## 11. 2024 Holdout Results (Final Evaluation � Evaluated Once, No Retraining)

> These are the definitive, final results.
> No retraining or tuning was performed after seeing 2024 outcomes.

| Metric | Value |
|---|---|
| **MAE** | **230.75 kg/ha** |
| **RMSE** | **321.45 kg/ha** |
| **R2** | **-0.6360** |
| **MAPE** | **41.69%** |

---

## 12. Previous-Year Baseline � 2024 Holdout

| Metric | Value |
|---|---|
| MAE | 189.86 kg/ha |
| Model beats this baseline | **NO** (model MAE 230.75 > baseline 189.86) |

The Previous-Year baseline uses each district's actual 2023 yield as the 2024 prediction.
The model does NOT beat this baseline on 2024. This is honest and must be reported as-is.

---

## 13. Historical-Mean Baseline � 2024 Holdout

| Metric | Value |
|---|---|
| MAE | 281.18 kg/ha |
| Model beats this baseline | **YES** (model MAE 230.75 < baseline 281.18) |

---

## 14. Per-District 2024 Predictions

| District | Actual (kg/ha) | Predicted (kg/ha) | Error (kg/ha) | MAPE |
|---|---|---|---|---|
| Akola | 261.49 | 396.12 | -134.63 | 51.49% |
| Amravati | 572.00 | 411.13 | +160.87 | 28.12% |
| Buldhana | 280.83 | 439.28 | -158.45 | 56.42% |
| Nagpur | 390.35 | 509.12 | -118.77 | 30.43% |
| Wardha | 462.37 | 344.35 | +118.02 | 25.53% |
| Washim | 550.24 | 403.24 | +147.00 | 26.72% |
| **Yavatmal** | **1,063.00** | **285.48** | **+777.52** | **73.14%** |

### Yavatmal 2024 Diagnosis
Yavatmal's actual 2024 yield (1,063 kg/ha) was approximately 2.7x its 2023 yield.
Lag features anchored predictions to the low 2023 district base (~389 kg/ha).
The model could not predict this structural break.
Yavatmal accounts for ~54% of total absolute error across all 7 districts.

If Yavatmal is excluded (for reference only � it must NOT be removed):
- Remaining 6-district average absolute error: ~139.7 kg/ha
- Remaining 6-district average MAPE: ~36.4%

**Do not remove Yavatmal from the dataset or evaluation.**

---

## 15. SHAP / XAI Status

**Status:** WORKING
**Method:** `shap.TreeExplainer(GradientBoostingRegressor)`
**Base value (expected model output):** 230.73 kg/ha
**SHAP reconstruction error:** 0.0000 kg/ha (exact)
**Verified on:** 2024 holdout samples (7 rows)

### Top 15 Features by Mean |SHAP| (computed on 2024 holdout)

| Rank | Feature | Mean |SHAP| (kg/ha) |
|---|---|---|
| 1 | rolling_3yr_yield_mean_kg_ha | 144.70 |
| 2 | tmin_min_c | 25.69 |
| 3 | tmax_max_c | 12.98 |
| 4 | tmax_annual_mean_c | 8.75 |
| 5 | rainfall_annual_mm | 8.15 |
| 6 | tmax_hot_days_ge35_kharif | 7.05 |
| 7 | tmax_kharif_mean_c | 6.63 |
| 8 | rainy_days_monsoon | 5.90 |
| 9 | cotton_area_000ha | 5.40 |
| 10 | tmin_annual_mean_c | 5.18 |
| 11 | rainfall_monsoon_mm_district_anomaly | 4.82 |
| 12 | rainfall_monsoon_mm | 4.14 |
| 13 | max_dry_spell_annual_days | 3.57 |
| 14 | tmin_kharif_mean_c | 3.11 |
| 15 | rainfall_kharif_mm | 2.97 |

Note: Feature importance shows statistical association, not causation.

---

## 16. Exact Artifact Paths

All paths relative to project root:
`C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI/`

### ML Artifacts (Production � loaded by backend)

| Artifact | Relative Path | Notes |
|---|---|---|
| Full sklearn Pipeline | `backend/ml/artifacts/final_model.pkl` | Trained 1997-2023. Correct holdout. |
| Preprocessor only | `backend/ml/artifacts/preprocessor.pkl` | |
| Feature schema | `backend/ml/artifacts/feature_schema.json` | |
| Model metadata | `backend/ml/artifacts/model_metadata.json` | Updated with 2024 holdout metrics |
| Legacy pipeline | `backend/ml/artifacts/final_cotton_yield_model.joblib` | Trained 1997-2024. Currently loaded by cotton_predictor.py. |

### Validation Evaluation Outputs

| Artifact | Relative Path |
|---|---|
| 2024 holdout results | `backend/ml/evaluation/final/actual_vs_predicted_2024.csv` |
| 2024 district results | `backend/ml/evaluation/final/final_2024_district_results.csv` |
| Model comparison | `backend/ml/evaluation/final/model_comparison_2011_2023.csv` |
| Lag sensitivity | `backend/ml/evaluation/final/lag_sensitivity_2011_2023.csv` |
| Hyperparameter tuning log | `backend/ml/evaluation/final/tuning_GradientBoosting.csv` |
| SHAP feature importances | `backend/ml/evaluation/final/shap_feature_importance.csv` |
| Selected model config | `backend/ml/evaluation/final/selected_model_config.json` |
| Final Validation Report | `backend/ml/evaluation/final/FINAL_MODEL_VALIDATION_REPORT.md` |
| 2024 holdout bar chart | `backend/ml/evaluation/final/plots/actual_vs_predicted_2024.png` |
| Selection folds scatter | `backend/ml/evaluation/final/plots/selection_actual_vs_predicted.png` |

### ML Scripts

| Script | Purpose |
|---|---|
| `backend/ml/final_model_selection.py` | **Authoritative** � full 17-phase pipeline with strict 2024 holdout |
| `backend/ml/training/train_models.py` | Original training script (uses 2011-2024 folds � superseded) |
| `backend/ml/cotton_predictor.py` | Loads model, runs SHAP, serves predictions to API |
| `backend/ml/run_model_validation.py` | Earlier validation (2011-2024 folds � superseded) |
| `backend/ml/run_model_diagnostics.py` | Feature audit and diagnostic charts |
| `backend/ml/evaluation/test_prediction.py` | CLI test of a single prediction |

---

## 17. Backend Status

**Framework:** FastAPI + Uvicorn
**Host:** 127.0.0.1
**Port:** 8000

**Key Routes:**

| Route | Method | Purpose |
|---|---|---|
| `/api/health` or `/` | GET | Health check, model status |
| `/api/cotton/predict` | POST | Cotton yield prediction + SHAP |
| `/docs` | GET | Swagger UI |

**Model loaded at startup:** `final_cotton_yield_model.joblib` (trained 1997-2024)
**Remaining task:** Update `cotton_predictor.py` to load `final_model.pkl` (trained 1997-2023) instead.

---

## 18. Frontend Status

**Framework:** React + Vite
**Port:** 5173
**API URL:** `http://127.0.0.1:8000` (configurable via `VITE_API_URL` env var)

**Pages:**

| Route | Page |
|---|---|
| `/` | Landing Page |
| `/dashboard` | Dashboard (KPI, yield trend, district comparison) |
| `/predict` | Cotton Yield Prediction (5-step stepper + SHAP display) |
| `/insights` | Model Insights (metrics, feature importance) |
| `/weather` | Weather Overview |
| `/history` | Historical Data (yield/rainfall/temperature charts) |
| `/recommendations` | Advisory Recommendations |
| `/about` | About / Methodology |

---

## 19. Remaining Tasks

### High Priority
- [ ] Update `backend/ml/cotton_predictor.py` to load `final_model.pkl` (1997-2023)
  instead of `final_cotton_yield_model.joblib` (1997-2024). This is required for
  methodological correctness when the app predicts future years.

- [ ] Update `/api/health` in `backend/main.py` to reflect `training_years: 1997-2023`
  and correct validation metrics from `model_metadata.json`.

### Medium Priority
- [ ] Update `ModelInsightsPage.jsx` to display SHAP-based feature importances
  from `shap_feature_importance.csv` instead of Gini-based importances.

- [ ] Wire `actual_vs_predicted_2024.png` into the Model Insights or About page.

### Low Priority
- [ ] Add `/api/cotton/validation` endpoint to serve 2024 holdout results as JSON.
- [ ] Add district-level error breakdown component to the frontend.
- [ ] Freeze `requirements.txt` to lock package versions.

### Do NOT Do
- Do not modify the authoritative dataset.
- Do not retrain the model.
- Do not remove Yavatmal.
- Do not hide the 2024 holdout results or the baseline comparison.
- Do not describe MAE as a confidence interval.
- Do not call R2 accuracy.
- Do not fabricate SHAP values.
- Do not claim causation from feature importance.

---

## 20. Commands to Run the Project

### Start the Backend
```bash
cd C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
URL: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

### Start the Frontend (separate terminal)
```bash
cd C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI/frontend
npm run dev
```
URL: http://localhost:5173

### Re-run Final Model Selection (only if needed)
```bash
cd C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI
python backend/ml/final_model_selection.py
```
Takes ~3-5 minutes. Runs all 17 phases. 2024 holdout integrity maintained.

### Test a Single Prediction via CLI
```bash
cd C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI
python backend/ml/evaluation/test_prediction.py
```

### Build Frontend for Production
```bash
cd C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI/frontend
npm run build
```

---

## 21. Key Interpretation Rules

1. **MAE is not a confidence interval.**
   Correct: 'The model mean MAE was 106.18 kg/ha on 2011-2023 folds.'
   Incorrect: 'Predictions are accurate to +/-106 kg/ha.'

2. **R2 is not accuracy.** Do not call R2 a percentage accuracy.

3. **Negative R2** does not mean the model is useless. On 2011-2023 folds,
   the model beats both baselines on MAE, which is the primary evaluation metric.

4. **The model does not beat the Previous-Year baseline on 2024.**
   Model MAE: 230.75 kg/ha. PrevYear MAE: 189.86 kg/ha.
   This is honest and must not be concealed or minimized.

5. **Feature importance shows statistical association, not causation.**

6. **SHAP values are real.** TreeExplainer reconstruction error = 0.0000 kg/ha.

7. **Yavatmal 2024 is a structural break**, not a model failure.
   The 2.7x yield surge from 2023 to 2024 is not predictable from prior-year lag features.
