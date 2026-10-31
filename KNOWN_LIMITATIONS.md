# AgriPredict-AI — Known Technical & Scientific Limitations

**Document Type:** Scientific Integrity & Boundary Disclosure Report  
**System Name:** AgriPredict-AI  
**Audience:** Academic Evaluation Committee, Agricultural Data Scientists  
**Status:** Approved for Demonstration  

---

## 1. Principle of Scientific Honesty

In academic machine learning projects, it is common to encounter claims of "95% accuracy" on agricultural yield prediction. In real-world agricultural economics and meteorological science, such claims are almost universally the result of **data leakage**, **lookahead bias**, **unprincipled synthetic oversampling**, or **evaluating models on trivial non-chronological random splits**.

AgriPredict-AI is built on authentic empirical data from the Indian Meteorological Department (IMD) and Maharashtra State Agricultural Department records. This document explicitly outlines the known limitations, operational assumptions, and boundary conditions of our platform.

---

## 2. Key Technical & Operational Limitations

### 2.1 Geographic Boundary (6 Vidarbha Districts)
- **Constraint:** Cotton yield prediction is strictly restricted to six contiguous districts in Vidarbha: **Akola, Amravati, Buldhana, Nagpur, Wardha, and Washim**.
- **Exclusion of Yavatmal:** Although Yavatmal is traditionally considered the cotton capital of Vidarbha, an in-depth data audit revealed historical taluka bifurcation shifts, inconsistent reporting conventions, and abrupt multi-fold variances in official yield series that lacked biophysical weather correlation. Including Yavatmal degraded overall model stability; it was therefore systematically excluded to preserve data integrity.
- **Exclusion of Western Maharashtra / Konkan:** Regions outside Vidarbha have fundamentally different agro-ecological zones (e.g., sugarcane belts under canal irrigation, or coastal rice paddies) and cannot be modeled using rainfed cotton parameterizations.

### 2.2 Spatial Resolution (District-Level vs. Farm-Level)
- **Constraint:** Official government historical yield records are aggregated at the **district level**.
- **Real-World Impact:** An individual district spans thousands of square kilometers. A farmer in northern Akola (Telhara taluka) may experience 120 mm of localized downpour, while a farmer in southern Akola (Patur taluka) experiences drought. AgriPredict-AI predicts the **macro-district mean yield**; it does not account for micro-topographical farm-level variations without on-site sensor telemetry.

### 2.3 Sample Size Realities ($N = 194$ Observations)
- **Constraint:** Across 28 years (1997–2024) and 6 districts, the canonical panel consists of exactly **194 district-year observations**.
- **Methodological Impact:** This small-sample regime strictly rules out data-hungry deep learning architectures (e.g. LSTMs, Transformers, Deep MLPs), which severely overfit on $N < 200$. Linear models with $L_2$ regularization (Thermal Ridge) and constrained decision trees are mathematically the only defensible approaches.

### 2.4 Unmodeled Biological Dynamics (Pests & Diseases)
- **Constraint:** Pests such as the **Pink Bollworm (*Pectinophora gossypiella*)**, American bollworm, and whiteflies are major determinants of cotton loss in Vidarbha.
- **Limitation:** Historical district yield series do not contain structured, standardized annual trap catch or infestation percentage records. In anomalous years such as 2017—where a catastrophic pink bollworm outbreak devastated crops despite moderate rainfall—the model under-predicts the damage because the damage was biological rather than purely meteorological.

### 2.5 Remote Sensing Cloud-Cover Bottlenecks
- **Constraint:** Optical satellite imagery (Sentinel-2, Landsat) provides valuable vegetation indices (NDVI, NDRE).
- **Limitation:** In Vidarbha, the critical vegetative and flowering phases of cotton occur in July, August, and early September—the peak of the Southwest Monsoon. Optical satellite images during these months frequently suffer from 70% to 100% cloud cover. While MODIS and SMAP coarse-resolution radar data offer partial insight, cloud-free optical vegetation indices are intermittent.

### 2.6 Honest Performance Metrics & Residual Variance
- **Reported Thermal Ridge Cross-Validation Metrics (2011–2023, 13 Folds):**
  - **Mean Absolute Error (MAE):** `104.75 kg/ha`
  - **Root Mean Squared Error (RMSE):** `138.10 kg/ha`
  - **Weighted Absolute Percentage Error (WAPE):** `32.28%`
  - **Coefficient of Determination ($R^2$):** `0.2305`
  - **Predictions within $\pm 10\%$ of Actual:** `20.5%`
- **Interpretation:** Agricultural yield prediction under purely rainfed conditions contains significant irreducible noise ($\sim 30\%$). Our model provides substantial directional intelligence and risk forecasting, but cannot predict exact harvest weights down to the single kilogram.

### 2.7 Operational Forecast Timing Boundary (Post-Monsoon Pre-Harvest)
- **Constraint:** Cotton yield models incorporate realized in-season Kharif weather features through **October 31** (cumulative rainfall, rainy days, hot days $\ge 35^\circ\text{C}$, and diurnal temperature range).
- **Operational Reality:** The system is strictly a **Post-Monsoon Pre-Harvest Yield Estimator and Decision Support System for Six Vidarbha Districts**. It cannot function as a pre-sowing planting advisor in May/June because the required monsoon indices do not exist at that time.
- **Leakage Safeguard:** Calling the model before October 31 requires realized weather inputs and would introduce severe temporal look-ahead leakage.

### 2.8 Prediction Uncertainty & Calibration Realities
- **Empirically Calibrated Out-of-Fold Error Bounds ($\pm 253.5\text{ kg/ha}$):** The prediction interval represents empirical error bounds from 2011–2023 out-of-fold residuals, NOT a theoretical Gaussian or distribution-free guaranteed 90% confidence interval.
- **Proof of Retrospective Circularity:** In Phase 17, the reported 92.3% coverage across 2011–2023 ($N=78$) was derived using the 72nd order statistic ($k = \min(78, \lceil 79 \times 0.90 \rceil) = 72$). Evaluating this threshold on the same 78 residuals guarantees $72/78 = 92.307\%$ coverage by construction (a descriptive tautology).
- **Strict Rolling-Origin Prequential Calibration:**
  - In an expanding chronological window (calibrating year $t$ using only residuals $< t$):
    - 2011 and 2012 cannot be calibrated prospectively due to finite-sample quantile requirements ($N_{\text{prior}} = 0$ and $N_{\text{prior}} = 6 < 10$, where $k = \lceil 7 \times 0.90 \rceil = 7 > 6$).
    - Over all eligible forecast years (2013–2023, $N=66$), prospective rolling-origin calibration achieved **87.9% empirical coverage**.
    - During the 2016 bumper post-drought surge, prior drought years (2014 & 2015) contracted the threshold to $205.4\text{ kg/ha}$, resulting in an empirical coverage crash to **16.7%** (5 out of 6 districts breached the bound).
- **Independent 2024 Holdout:** Covered 6/6 observations ($100.0\%$), but $N=6$ is statistically insufficient to prove long-term coverage guarantees.
- **Asymmetric Interval Geometry:** The signed error distribution ($y - \hat{y}$) has a heavy positive tail (underprediction up to $+433.6\text{ kg/ha}$) and a truncated negative tail ($-281.9\text{ kg/ha}$). Asymmetric quantile bounds ($[-156.5, +258.1]\text{ kg/ha}$) have a total width of $414.6\text{ kg/ha}$ ($156.5 + 258.1$), achieving a **$92.4\text{ kg/ha}$ reduction in width** compared to symmetric $\pm 253.5\text{ kg/ha}$ ($507.0\text{ kg/ha}$) while achieving 89.7% coverage.
- **District & High-Yield Regime Variance:** Amravati exhibits elevated historical variance (76.9% coverage), and high-yield harvests ($>450\text{ kg/ha}$) experience increased breach rates due to $L_2$ shrinkage toward historical anchors. Active warning badges in the UI explicitly notify farmers of these boundary conditions.

---

## 3. Recommended Guidance for Demonstrations

When faculty or external examiners review the system:
1. Proudly acknowledge these limitations as evidence of scientific maturity.
2. Emphasize that knowing *where a model fails* is the hallmark of professional data engineering.
3. Show how SHAP waterfall explanations make these boundaries visible to users.
