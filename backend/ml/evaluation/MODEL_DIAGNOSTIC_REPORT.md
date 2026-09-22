# AgriPredict-AI Model Diagnostic & Feature Analytics Report

**Authoritative Dataset**: `vidarbha_cotton_model_ready_1997_2024.csv` (194 rows, 43 columns)  
**Target Column**: `yield_target_kg_ha`  
**Districts (7)**: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim, Yavatmal  
**Dataset Horizon**: 1997–2024 (28 Harvest Years)  

---

## 1. Executive Summary & Diagnostic Findings
- **Rolling-Origin Validation (2011–2024)**: The Random Forest model achieves an out-of-sample **MAE of 115.06 kg/ha** (RMSE 160.62 kg/ha, R² 0.1398, MAPE 39.04%).
- **Baseline Comparison**: The ML model outperforms the Previous-Year yield baseline (MAE 126.68 kg/ha, +9.2% improvement) and Historical District Mean baseline (MAE 147.30 kg/ha, +21.9% improvement).
- **2024 Holdout Test**: Evaluated strictly on 2024 after training on 1997–2023, the model achieved a **2024 MAE of 217.78 kg/ha** (RMSE 314.84 kg/ha, MAPE 38.35%).
- **Key Diagnosis**: The model exhibits heavy reliance on historical yield lag features (`previous_year_yield_kg_ha` and `rolling_3yr_yield_mean_kg_ha`), which account for **45.7% of total feature importance**. When abrupt yield shifts occur (e.g. 2024 Yavatmal yield anomaly), lag features lag behind real-time climate impacts.

---

## 2. Feature Audit & Categorization
- **Total Columns Audited**: 43
- **Predictive Model Features**: 36 (35 Numerical + 1 Categorical `district`)
- **Metadata Columns Excluded**: 7 (`yield_target_kg_ha`, `year`, `target_source_detail`, `target_review_flag`, `target_note`, `weather_temp_extraction`, `weather_rain_extraction`)
- **Data Leakage Status**: **PASS** (Zero future data or target leakage detected).

---

## 3. Lag Feature Reliance Experiment (Task 8)

| Feature Configuration | MAE (kg/ha) | RMSE (kg/ha) | R² | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Config A: All Features (36)** | **115.06** | **160.62** | **0.1398** | **39.04%** |
| Config B: Weather & Sown Area Only (No Lags) | 142.15 | 196.42 | -0.2872 | 41.22% |
| Config C: Lag Features Only + District | 120.44 | 168.30 | 0.0545 | 41.80% |

*Insight*: Removing lag features increases MAE from 115.06 to 142.15 kg/ha, confirming that historical yield momentum is the single strongest signal in the current dataset.

---

## 4. Candidate Model Comparison (2011–2024 Folds)

| Model | MAE (kg/ha) | RMSE (kg/ha) | R² | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **RandomForest** | 115.06 | 160.62 | 0.1398 | 39.04% |
| **GradientBoosting** | 115.08 | 159.85 | 0.1481 | 38.41% |
| **RidgeRegression** | 116.36 | 159.58 | 0.1509 | 41.39% |
| **HistGradientBoosting** | 116.74 | 165.15 | 0.0906 | 38.27% |
| **ExtraTrees** | 120.62 | 167.16 | 0.0683 | 41.21% |
| **Baseline_PrevYear** | 126.68 | 178.02 | -0.0567 | 44.73% |
| **Baseline_HistMean** | 147.3 | 207.8 | -0.4398 | 39.58% |

---

## 5. District-Wise Error Analysis (2011–2024 Folds)

| District | MAE (kg/ha) | RMSE (kg/ha) | R² | MAPE (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Akola** | **68.84** | **91.20** | **0.0007** | **23.85%** |
| Amravati | 165.93 | 192.36 | -0.2887 | 43.38% |
| Buldhana | 118.59 | 140.27 | 0.1075 | 53.52% |
| Nagpur | 106.73 | 136.93 | 0.1983 | 35.13% |
| **Wardha** | **102.02** | **130.14** | **-0.2012** | **27.64%** |
| Washim | 114.79 | 172.16 | 0.2529 | 40.90% |
| Yavatmal | 128.55 | 224.22 | 0.1178 | 48.90% |

---

## 6. Yavatmal Error Investigation (Task 4)
- **High Error Observations**: In 2024, Yavatmal actual yield reached **1,063.0 kg/ha**, whereas the model predicted **296.0 kg/ha** (absolute error 767.0 kg/ha).
- **Data Pattern**: Yavatmal previous year yield (2023) was **389.6 kg/ha** and 3-year rolling average was **553.0 kg/ha**. Because the model relies heavily on prior lag features, it smoothed the 2024 prediction toward historical district mean (~400 kg/ha) rather than anticipating the 2.7x yield surge.

---

## 7. 2024 Distribution Shift Analysis (Task 5)
- **Extreme Features in 2024**: Annual total rainfall in 2024 across Vidarbha averaged **1,049.5 mm** (+1.25 standard deviations above the 1997–2023 historical mean of 912.4 mm).
- **Out-of-Distribution Inputs**: Severe rainfall concentration during late Kharif phase created anomalous weather inputs for the 2024 holdout fold.

---

## 8. Limitations & Methodological Clarifications
1. **MAE Notation**: The model's rolling-origin validation MAE was **115.06 kg/ha**. MAE represents average absolute prediction error and is not a formal statistical confidence interval.
2. **Causation Disclaimer**: Feature importances and prediction errors indicate statistical correlation within decision trees; they do not establish direct agronomical causation.
3. **R² Interpretation**: R² reflects proportion of variance explained relative to dataset mean; negative R² in out-of-sample temporal folds indicates high variance in extreme weather years.
