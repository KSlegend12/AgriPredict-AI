# AgriPredict-AI — Final College Project Demonstration Script

**Document Type:** Spoken Presentation Script & Stage Directions  
**Target Duration:** 8 to 10 Minutes  
**Demonstration Date:** November 2, 2026  
**Audience:** Internal Faculty Guide, Department Head, External University Examiner  
**Location / System:** Windows 10/11 Local Machine (`http://127.0.0.1:5173`)  

---

## Pre-Demonstration Checklist (T-minus 5 Minutes)

Before calling the evaluators over, ensure your environment is primed:
1. **Terminal 1 (Backend):**
   ```powershell
   cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI"
   uvicorn backend.main:app --reload --port 8000
   ```
   *Verify:* Terminal prints `Application startup complete.`
2. **Terminal 2 (Frontend):**
   ```powershell
   cd "C:\Users\karta\.gemini\antigravity\scratch\AgriPredict-AI\frontend"
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
   *Verify:* Terminal prints `Local: http://127.0.0.1:5173/`
3. **Browser:** Open `http://127.0.0.1:5173` in Google Chrome or Edge. Maximize the window (`F11` for full screen if desired).
4. **Internet Status Check:** Check if the machine is connected to internet. If disconnected, note that AgriPredict-AI's built-in 3-tier fallback will automatically supply regional climatological telemetry without any errors.

---

## Demonstration Script & Timeline (8–10 Minutes)

### Phase 1: Introduction, Problem Statement & Objectives (0:00 – 1:45)
**Screen Display:** Landing Page (`/`)

> **Presenter (Spoken):**  
> *"Good morning respected examiners and faculty members. Today, we are proud to present **AgriPredict-AI**, an Explainable AI Decision Support System engineered specifically for the rainfed cotton farming belt of Vidarbha, Maharashtra.*
>
> *Across Maharashtra, particularly in the six Vidarbha districts—**Akola, Amravati, Buldhana, Nagpur, Wardha, and Washim**—cotton is the lifeline for millions of smallholder farmers. However, Vidarbha's agriculture is over 85% rainfed. Farmers face erratic monsoon onset, prolonged mid-season dry spells, and severe heatwaves during critical flowering and boll-setting stages. In dry years, yields plummet below 250 kg per hectare; in favorable years, they surge past 440 kg per hectare. This high variance drives debt cycles and agricultural distress.*
>
> *Our project objective was to build a production-grade, end-to-end platform that provides:*
> 1. *Pre-season and mid-season cotton yield intelligence grounded in verified historical data.*
> 2. *Explainable AI using SHAP so every estimate is transparent, showing the exact biophysical drivers.*
> 3. *Crop diversification advisory to recommend resilient alternative horticultural crops.*
> 4. *Future climate scenario modeling through 2031.*
>
> *Critically, we approached this project with scientific rigor: we do not claim unrealistic 95% accuracy on small-sample historical data. We report honest, reproducible error metrics and preserve an untouched 2024 holdout evaluation year."*

---

### Phase 2: Technology Stack Overview (1:45 – 2:30)
**Screen Display:** Landing Page — Point to System Snapshot metrics, then click **"Open Dashboard"**.

> **Presenter (Spoken):**  
> *"Before diving into the modules, here is our architectural foundation:*
> - *The **Frontend** is built with **React 18, Vite, and Tailwind CSS**, with interactive SVG charts rendered using **Recharts**.*
> - *The **Backend** is powered by **FastAPI (Python 3.13)** with asynchronous ASGI endpoints, validated strictly by **Pydantic V2 schemas**.*
> - *Our **Machine Learning Core** uses a dual-model architecture: a production Gradient Boosting baseline, and our specialized **Candidate Six-District Thermal Ridge model**, regularized against extreme Kharif temperatures.*
> - *Explainability is powered by closed-form **SHAP (SHapley Additive exPlanations)**.*
> - *Persistence is maintained through an ACID-compliant **SQLite database** logging every decision audit trail."*

---

### Phase 3: Regional Command Dashboard Walkthrough (2:30 – 3:45)
**Screen Display:** Main Dashboard (`/dashboard`)

> **Presenter (Stage Direction):**  
> 1. Click on the **District Selector** at the top right of the dashboard.
> 2. Switch from **Akola** to **Amravati**, then to **Nagpur**.
> 3. Point to the **Historical Yield & Rainfall Trendline** graph.

> **Presenter (Spoken):**  
> *"Here on the Regional Command Dashboard, the system gives agricultural extension officers and farmers instant macro-level visibility. When I switch districts from Akola to Nagpur, the entire dashboard reactively updates.*
>
> *Notice the 28-year historical trajectory from 1997 to 2024. You can clearly see the historic 2015 drought dip, followed by peak recoveries in 2021 and 2023. Below, our five unified quick-action cards provide direct pathways into Cotton Yield Prediction, Crop Advisory, Live Weather, Audit History, and Future Climate Scenarios."*

---

### Phase 4: Weather & Crop Diversification Advisory (3:45 – 5:15)
**Screen Direction:** Click **"Crop Advisory"** (`/recommend`) on the navbar.

> **Presenter (Stage Direction):**  
> 1. Click the button **"Auto-Fill Akola Benchmarks"**.
> 2. Show the soil chemistry fields populate: Nitrogen (80), Phosphorus (45), Potassium (40), pH (7.2), Moisture (55%), Temperature (28.5°C), Rainfall (780 mm).
> 3. Ensure sub-tab is on **"Multi-Crop Suitability"** and click **"Analyze Soil & Recommend Optimal Crops"**.

> **Presenter (Spoken):**  
> *"One major recommendation from agricultural universities like Dr. PDKV Akola is crop diversification to mitigate single-crop cotton failure. On the Crop Advisory page, we integrated trained Random Forest classification and regression models.*
>
> *By clicking 'Auto-Fill Akola Benchmarks', the system loads verified regional soil chemistry and climatic averages. When we run the recommendation, our multi-class model evaluates diversification candidates—**Onion, Tomato, and Sugarcane**.*
>
> *(Point to result)* *Here, Onion is identified as the optimal crop with an 88% suitability match, projecting a harvest of 17.5 tonnes per hectare under these soil parameters.*
>
> *If the farmer wishes to cultivate a specific cash crop, we switch to **Target Crop Yield Predictor**, enter the landholding (e.g. 2.5 Hectares of Tomato), and the regression model estimates the total expected tonnage."*

---

### Phase 5: Cotton Yield Prediction & Thermal Model (5:15 – 6:30)
**Screen Direction:** Click **"Cotton Yield"** (`/cotton`) on the navbar.

> **Presenter (Stage Direction):**  
> 1. Select District: **Akola**.
> 2. Select Harvest Year: **2024** (the untouched holdout year).
> 3. Ensure Model Candidate is **"Candidate Six-District Thermal Ridge"**.
> 4. Click **"Run Prediction"**.

> **Presenter (Spoken):**  
> *"Now we move to our core innovation: **Cotton Yield Prediction**.*
>
> *We select Akola and target year 2024. In the background, our `cotton_input_builder` extracts authentic IMD rainfall, Kharif maximum temperature extremes, and historical multi-year lag yields.*
>
> *Notice the predicted yield:* **444.4 kg/ha**.
>
> *Why did we deploy the **Thermal Ridge candidate** here? Standard models suffer from extreme swings when encountering anomalous heat. Our Thermal Ridge model introduces biophysical shrinkage on extreme temperatures (`tmax_kharif_mean_c`), anchoring predictions against a 3-year rolling regional yield baseline. Across 13-fold chronological cross-validation from 2011 to 2023, this model achieved a Mean Absolute Error of 104.75 kg/ha and a WAPE of 32.28%."*

---

### Phase 6: Explainable AI & SHAP Waterfall (6:30 – 7:30)
**Screen Direction:** Scroll directly down to the **"Why This Prediction? (SHAP Breakdown)"** component.

> **Presenter (Stage Direction):**  
> Point to the waterfall steps and explain the contributions.

> **Presenter (Spoken):**  
> *"In agriculture, a black-box number is dangerous. An extension officer needs to know WHY the model predicts 444 kg/ha.*
>
> *Here, our closed-form SHAP engine decomposes the prediction step-by-step:*
> 1. *It begins with the **Historical 3-Year Rolling Average Anchor** of **391.9 kg/ha**.*
> 2. *The **Biophysical Calibration Baseline** adds **+44.9 kg/ha**, establishing a base expectation of 436.8 kg/ha.*
> 3. *Then, individual climatic factors act upon the crop: **Monsoon Rainy Days** contributes **+8.3 kg/ha**, showing favorable precipitation distribution.*
> 4. *Conversely, the **Previous 2-Year Cotton Yield** subtracts **-21.4 kg/ha**, accounting for soil nutrient depletion and pest cycles.*
>
> *The sum of all SHAP attributions exactly equals the final predicted yield of 444.4 kg/ha. This gives farmers complete transparency."*

---

### Phase 7: Future Climate Forecasting (2026–2031) (7:30 – 8:30)
**Screen Direction:** Click **"Future Forecast"** (`/future-forecast`) on the navbar.

> **Presenter (Stage Direction):**  
> Select **Akola** or **Nagpur**, and point to the 3 scenario curves.

> **Presenter (Spoken):**  
> *"Looking forward, climate change is shifting Kharif monsoon patterns. Our Future Forecast module projects cotton yields from 2026 to 2031 under three IPCC-aligned agronomic scenarios:*
> - *The **Baseline scenario** projects steady yields around 430–450 kg/ha.*
> - *The **Dry Kharif scenario** (-15% rainfall, +1.5°C temperature) indicates severe yield depression down to 340 kg/ha.*
> - *The **Wet Kharif scenario** (+20% rainfall) shows moderate gains, capped by waterlogging risks.*
>
> *This provides long-term risk assessment for regional policymakers and insurance planners."*

---

### Phase 8: Audit Trail, Conclusion & Future Scope (8:30 – 9:30)
**Screen Direction:** Click **"History"** (`/history`) on the navbar.

> **Presenter (Stage Direction):**  
> Point to the latest rows in the SQLite prediction audit table.

> **Presenter (Spoken):**  
> *"Finally, we visit the **Audit Trail & History** tab. Every prediction we executed today—both our 444.4 kg/ha Cotton prediction and our Horticultural Onion recommendation—has been persisted into SQLite with exact timestamps, input features, and models.*
>
> *Notice our harmonized unit representation: Cotton is displayed in **kg/ha**, while horticultural crops are displayed in **tonnes/ha**.*
>
> *In summary, AgriPredict-AI bridges advanced machine learning, agro-meteorological science, and full-stack software engineering into a practical decision support system.*
>
> *For future work, we plan to incorporate high-resolution Sentinel-2 satellite vegetation indices (NDVI/NDRE) once cloud-penetrating synthetic aperture radar (SAR) feeds are integrated, and deploy an offline-first mobile PWA for field workers.*
>
> *Thank you. We are now eager to answer your questions."*

---

## Backup Demonstration Plan (Contingency Scenarios)

| Scenario / Risk | Potential Impact | Automated System Mitigation & Presenter Action |
| :--- | :--- | :--- |
| **Complete Internet Disconnection** | External weather APIs (OpenWeatherMap / Open-Meteo) fail to respond. | **Built-in System Mitigation:** `weather_service.py` catches timeout/connection errors and immediately falls back to regional Vidarbha climatological averages (`is_live_api: False`). The UI remains 100% functional without errors.<br>**Presenter Action:** Say: *"Our system is architected with a 3-tier fallback. If internet drops in rural areas, it seamlessly transitions to regional climatological baselines."* |
| **Port Conflict on 8000 or 5173** | Server fails to bind. | **Presenter Action:** Run PowerShell kill command from `PROJECT_RUN_GUIDE.md`: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess \| Stop-Process -Force`. |
| **Database Lock or Corrupt File** | SQLite file blocked. | **Presenter Action:** Delete `backend/agripredict.db`. The FastAPI lifespan handler recreates clean tables automatically on startup. |
| **Examiner Requests an Unsupported District (e.g. Pune or Yavatmal)** | Cotton prediction rejects request. | **Presenter Action:** Show that the UI and API enforce data governance by design: *"We deliberately restrict cotton yield to the 6 verified Vidarbha districts because cotton is an agro-climatic specialist crop in Maharashtra. Yavatmal was excluded due to verified historical reporting anomalies."* |
