# AgriPredict-AI — College Demonstration Walkthrough Script

**Demonstration Date:** November 2, 2026  
**Audience:** Academic Evaluation Committee, External Examiners & Project Supervisors  
**Project Title:** AgriPredict-AI: Multi-Modal Agricultural Decision Support & Cotton Yield Prediction  
**Demonstration Time:** Approximately 10–12 Minutes  
**Primary URL:** `http://127.0.0.1:5173` (Frontend) & `http://127.0.0.1:8000` (Backend API)  

---

## Evaluation Presentation Strategy

When demonstrating AgriPredict-AI, emphasize **rigorous data science**, **authentic agronomic engineering**, and **production software quality** over exaggerated accuracy claims:
1. **Explain the Real Problem:** Vidarbha faces severe climate variability, erratic Kharif rainfall, and thermal stress during cotton flowering.
2. **Highlight Integrity:** 28 years of canonical historical data (1997–2024), strictly isolated 2024 holdout year, and zero synthetic target fabrication.
3. **Showcase Dual Capabilities:** Cotton yield intelligence (Thermal Ridge + SHAP) and Multi-crop diversification advisory (Random Forest Classifier + Regressor).

---

## 10-Step Interactive Evaluation Flow

```mermaid
flowchart LR
    A["1. Landing Page"] --> B["2. Dashboard"]
    B --> C["3. Cotton Yield"]
    C --> D["4. SHAP XAI"]
    D --> E["5. Crop Advisory"]
    E --> F["6. Crop Yield"]
    F --> G["7. Weather Agromet"]
    G --> H["8. Future Forecast"]
    H --> I["9. Model Insights"]
    I --> J["10. History Audit"]
```

---

### Step 1 — Project Landing Page (`/`)
- **Action:** Open `http://127.0.0.1:5173/` in full-screen mode.
- **What to highlight:**
  - Hero presentation of the 6 Vidarbha districts: **Akola, Amravati, Buldhana, Nagpur, Wardha, Washim**.
  - Key architectural indicators: 28 harvest years (1997–2024), 194 district-year observations.
  - Transparent model declaration: Gradient Boosting production baseline and Thermal Ridge candidate.
- **Examiner Talking Point:**  
  *"AgriPredict-AI was engineered specifically for the rainfed agro-ecosystems of Vidarbha. We do not claim fabricated 95% accuracy; instead, we provide actionable, scientifically grounded decision support based on verified IMD weather and agronomic data."*

---

### Step 2 — Regional Command Dashboard (`/dashboard`)
- **Action:** Click **"Open Dashboard"** or use the top navigation bar.
- **What to highlight:**
  - **District Switcher:** Toggle between *Akola*, *Amravati*, *Nagpur*, etc. Observe the immediate dynamic update of climate and historical yield trends.
  - **Historical Yield Chart:** Point out the historical variability (e.g. drought drops in 2015 vs peaks in 2021/2023).
  - **Quick Action Cards:** Demonstrate the 5 unified action cards providing one-click access across the entire platform.

---

### Step 3 — Cotton Yield Prediction (`/cotton`)
- **Action:** Click **"Cotton Yield"** on the navbar or dashboard.
- **Input Parameters:**
  - Select District: **Akola**
  - Select Target Year: **2024**
  - Model Candidate: **Candidate Six-District Thermal Ridge** (default user-facing candidate)
- **Click:** **"Run Prediction"**
- **What to highlight:**
  - Notice the instant prediction response (~270–290 kg/ha lint cotton yield).
  - Show how input weather features (annual rainfall, Kharif maximum temperature) and historical lag yields are automatically injected and validated.

---

### Step 4 — Explainable AI (SHAP Waterfall Visualization)
- **Action:** Scroll down immediately below the predicted yield card on `/cotton`.
- **What to highlight:**
  - **Waterfall Attribution Chart:** Show how the base value (regional mean yield) is pushed up or down by individual features.
  - **Thermal Feature Impact:** Highlight how high Kharif temperatures (`tmax_kharif_mean_c`) create heat stress penalties during boll development.
  - **Rainfall Dynamics:** Explain how monsoon volume impacts soil moisture retention in Vidarbha's deep black Vertisol soils.
- **Examiner Talking Point:**  
  *"Rather than operating as an uninterpretable black box, our model uses closed-form SHAP feature attributions so agricultural officers can inspect exactly why a specific yield estimate was produced."*

---

### Step 5 — Multi-Crop Suitability Advisory (`/recommend` — Mode 1)
- **Action:** Click **"Crop Advisory"** on the top navigation bar.
- **Interactive Action:**
  - Click **"Auto-Fill Akola Benchmarks"** (or another district). Watch all soil chemistry (N, P, K, pH, moisture) and weather parameters populate instantly.
  - Ensure the tab is on **"Multi-Crop Suitability"**.
  - Click **"Analyze Soil & Recommend Optimal Crops"**.
- **What to highlight:**
  - The model calculates suitability distributions across regional diversification crops (**Tomato, Onion, Sugarcane**).
  - Point out the primary recommended crop card with its percentage match, alongside comparative progress bars for secondary alternatives.

---

### Step 6 — Horticultural Crop Yield Predictor (`/recommend` — Mode 2)
- **Action:** Click on the second sub-tab: **"Target Crop Yield Predictor"**.
- **Interactive Action:**
  - Select Crop: **Tomato** (or Onion).
  - Enter Cultivated Land Area: **2.5 Hectares**.
  - Click **"Estimate Harvest Yield"**.
- **What to highlight:**
  - Display of predicted yield in **metric tonnes per hectare (t/ha)** and total projected farm output in tonnes.
  - Direct persistence into SQLite database with one-click link to review in the Audit Trail.

---

### Step 7 — Live Agro-Meteorological Advisory (`/weather`)
- **Action:** Click **"Weather"** on the navbar.
- **What to highlight:**
  - Current real-time temperature, relative humidity, wind speed, and precipitation.
  - 7-day meteorological forecast.
  - **Automated Agromet Bulletins:** Show district-specific operational alerts (e.g. drainage recommendations during heavy rainfall; spraying precautions for sucking pests and pink bollworm during high humidity).

---

### Step 8 — Future Climate Scenarios (2026–2031) (`/future-forecast`)
- **Action:** Click **"Future Forecast"** on the navbar.
- **What to highlight:**
  - Multi-year projections from 2026 to 2031 across 3 distinct climate scenarios:
    1. *Baseline Kharif:* Historical median monsoon rainfall and average temperature.
    2. *Dry Kharif Scenario:* -15% rainfall anomaly, +1.5°C thermal warming.
    3. *Wet Kharif Scenario:* +20% rainfall anomaly with moderate temperatures.
  - Visual trendlines illustrating long-term resilience and risk under climate variability.

---

### Step 9 — Model Methodology & Scientific Insights (`/insights`)
- **Action:** Click **"Model Insights"** on the navbar.
- **What to highlight:**
  - **Transparent Evaluation Metrics:** Review chronological cross-validation metrics (MAE: 104.75 kg/ha, WAPE: 32.28%, R²: 0.2305).
  - **Feature Importance Hierarchy:** Show the relative ranking of lag yield, Kharif temperature extremes, and seasonal rainfall.
  - **Error Audit Insights:** Discuss how the system accounts for outlier years without unprincipled data manipulation.

---

### Step 10 — Database Audit Trail & Verification (`/history`)
- **Action:** Click **"History"** on the navbar.
- **What to highlight:**
  - **Unified SQLite Log:** Show that the Cotton prediction from Step 3 and the Crop Yield prediction from Step 6 were recorded with timestamps, districts, models, and inputs.
  - **Harmonized Units:** Verify that cotton is logged in **kg/ha**, while horticultural crops are logged in **t/ha**.
  - **Interactive District Filter:** Demonstrate filtering logs by district.

---

## 3. Potential Evaluator Questions & Ready Answers

**Q1: Why did you exclude Yavatmal from the 6 target districts?**  
*Answer:* "During our rigorous data quality audit, historical reporting series for Yavatmal exhibited severe discontinuity and anomalous yield reporting shifts across bifurcated talukas. To maintain scientific integrity and prevent corrupted feature distributions, we scoped the model strictly to the 6 verified contiguous districts."

**Q2: Why not claim 95% accuracy like many student machine learning projects?**  
*Answer:* "Agricultural yield in rainfed Vidarbha is heavily influenced by unmeasured micro-climate events, localized pest outbreaks (such as pink bollworm), and harvest-stage weather shocks. Claiming 95% accuracy on small-sample historical yield data is almost always a result of target leakage or overfitted models. Our Thermal Ridge model achieves an honest, reproducible WAPE of 32.28% and MAE of 104.75 kg/ha under strict chronological cross-validation."

**Q3: How does the system handle explainability for non-technical farmers?**  
*Answer:* "We integrate closed-form SHAP attributions and convert mathematical delta values into plain-English agronomic summaries—explaining whether high temperatures, moisture deficits, or historical momentum drove the prediction."
