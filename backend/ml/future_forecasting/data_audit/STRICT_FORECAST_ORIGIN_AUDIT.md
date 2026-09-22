# Strict Forecast-Origin Audit — Cotton Yield 2027–2031 Module

## Scope
This audit evaluates whether the existing future-forecast artifact can support genuine future forecasting. It does **not** replace the validated 2024 model and does not modify the authoritative dataset.

## Key finding
The existing future artifact was built with target-year weather features available in its training feature schema. Those weather variables are not known at a real forecast origin. Therefore, the artifact's stored model-selection metrics are **not sufficient evidence of real-world forecast skill**.

The new audit creates a strict forecast-origin-safe hindcast using:
- historical origin year `o`
- target year `t = o + horizon`
- yield lags/rolling statistics calculated using data available at `o`
- target-year weather replaced by an origin-only 10-year climatology
- temperature projected using an origin-only linear historical trend
- expanding rolling-origin training: each test year is trained only on earlier target years
- test target years 2015–2024
- horizons 1–7
- baselines: previous-year yield

## Strict hindcast results

| Horizon | Random Forest MAE | Gradient Boosting MAE | Ridge MAE | Previous-year MAE |
|---:|---:|---:|---:|---:|
| 1 | 129.77 | 135.92 | 133.23 | 139.22 |
| 2 | 128.90 | 129.83 | 152.97 | 171.18 |
| 3 | 122.93 | 131.06 | 159.01 | 150.77 |
| 4 | 129.19 | 131.30 | 173.01 | 158.98 |
| 5 | 136.57 | 147.97 | 172.06 | 176.91 |
| 6 | 136.00 | 146.80 | 177.00 | 182.20 |
| 7 | 147.34 | 144.67 | 167.09 | 180.01 |

These values are MAE in kg/ha. They are **hindcast validation results**, not confidence intervals and not guarantees for 2027–2031.

## Five-year-use slice
For target years 2020–2024 and horizons 3–7:
- Random Forest: MAE 142.48 kg/ha, RMSE 194.97 kg/ha
- Gradient Boosting: MAE 142.20 kg/ha, RMSE 193.43 kg/ha
- Ridge: MAE 174.08 kg/ha, RMSE 224.02 kg/ha
- Previous-year baseline: MAE 216.95 kg/ha, RMSE 276.20 kg/ha

This slice is useful for judging the 3–7 year horizon regime, but it is still a historical simulation and not a 2027–2031 forecast guarantee.

## Important interpretation
The strict audit is materially different from the existing artifact's stored `horizon_model_selection.csv`. The existing artifact uses the same target-year weather feature schema for model training; a real forecast cannot observe those target-year weather values. The strict audit therefore uses an origin-only weather proxy and retrains inside each rolling-origin test step.

The strict audit is an **audit-only experiment**. It does not replace `future_horizon_models.joblib`, `final_model.pkl`, or the authoritative dataset.

## Current status
- Current validated 2024 model: unchanged.
- Authoritative 1997–2024 dataset: unchanged.
- Yavatmal: retained.
- Existing future artifact: retained, but not promoted to a scientifically validated production forecast model.
- Strict hindcast artifacts: stored under this `data_audit/` directory.

## Next required work
1. Rebuild the future model using the same forecast-origin-safe feature generation used in this audit.
2. Improve future weather inputs using actual historical forecast/reanalysis proxies where available, rather than only climatology.
3. Add 2025 and 2026 observed yield/weather data when authoritative sources are available, so the real 2027 forecast origin can use the latest state.
4. Compare multiple safe feature sets and models under the same rolling-origin protocol.
5. Only then generate the production 2027–2031 scenario forecasts.
