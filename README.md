# AgriPredict-AI

> **Post-Monsoon Pre-Harvest Cotton Yield Estimation and Decision Support System for Six Vidarbha Districts**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-298%20Passed-brightgreen.svg)](#testing-and-verification)

---

## 1. Project Overview

**AgriPredict-AI** is a **Post-Monsoon Pre-Harvest Cotton Yield Estimation and Decision Support System for Six Vidarbha Districts** (Akola, Amravati, Buldhana, Nagpur, Wardha, and Washim). It is built to assist agronomists, regional agricultural planners, and extension personnel in Maharashtra, India.

### Operational Forecast Origin & Timing Boundary
- **Forecast Horizon**: End-of-season yield estimation conducted in **October / early November**, prior to harvest.
- **In-Season Agro-Meteorological Realization**: The model requires cumulative Kharif rainfall, rainy days, extreme heat days ($\ge 35^\circ\text{C}$), and diurnal temperature range measured through **October 31**.
- **Important Boundary**: The system is **NOT** a pre-sowing prediction system, a May/June planting advisor, or a full-season forecast before monsoon observations exist. Running the model before Kharif weather realizes would constitute severe temporal leakage.
- **Longitudinal Evaluation**: Yield modeling across 28 harvest seasons (1997–2024), utilizing expanding-window chronological cross-validation, thermal and moisture stress interactions, explainable AI (SHAP) feature attribution, and empirical out-of-fold error bounds.

---

## 2. Target Geographic Scope

### Vidarbha Six-District Focus
The dedicated cotton yield forecasting module focuses strictly on six core agricultural districts in the Vidarbha region:
1. **Akola**
2. **Amravati**
3. **Buldhana**
4. **Nagpur**
5. **Wardha**
6. **Washim**

### Yavatmal Scope Isolation
- **Frontend & Candidate Scope**: Following empirical error audits and regional agrarian volatility analysis, Yavatmal was intentionally excluded from the candidate model development scope and completely removed from the frontend user interface.
- **Defensive API Guardrails**: API requests targeting Yavatmal under the six-district candidate models return `HTTP 422 Unprocessable Entity`.
- **Production Baseline Integrity**: The canonical historical dataset (`data/vidarbha_cotton_model_ready_1997_2024.csv`, SHA-256: `1430370e...`) and the production model artifact (`backend/ml/artifacts/final_model.pkl`, SHA-256: `3b0c2fda...`) preserve 7-district records to ensure backward compatibility and fair benchmarking.

---

## 3. System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │            React 18 + Vite Frontend          │
                    │   (Tailwind CSS, Lucide Icons, Recharts)     │
                    └───────────────────────┬──────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                    ┌──────────────────────────────────────────────┐
                    │             FastAPI Backend Engine           │
                    │          (Python 3.10+, Uvicorn Async)       │
                    └──────┬───────────────┬───────────────┬───────┘
                           │               │               │
            ┌──────────────▼────┐   ┌──────▼──────┐   ┌────▼──────────────┐
            │   Cotton Yield    │   │ Multi-Crop  │   │  Weather Service  │
            │ Prediction Module │   │ Suitability │   │ & History Tracker │
            └─────────┬─────────┘   └─────────────┘   └───────────────────┘
                      │
        ┌─────────────┴─────────────────────────┐
        ▼                                       ▼
┌───────────────────────────────┐   ┌───────────────────────────────────┐
│ Production Model (Default)    │   │ Thermal Ridge Candidate (Opt-In)  │
│ - Gradient Boosting Regressor │   │ - RobustScaler + Ridge (α=100)    │
│ - 36 Features (1997-2023)     │   │ - 38 Features (Thermal Delta)     │
│ - TreeExplainer SHAP          │   │ - Closed-Form Additive SHAP       │
└───────────────────────────────┘   └───────────────────────────────────┘
```

---

## 4. Key Features

- **Dual-Model Cotton Architecture**: Switch seamlessly between the production Gradient Boosting model (system default) and the research-grade Six-District Thermal Ridge candidate.
- **Closed-Form Explainable AI (SHAP)**: Waterfall attributions quantify the exact positive and negative contributions of extreme heat days, diurnal temperature range, and monsoon anomalies.
- **Live Agro-Meteorological Intelligence**: Real-time temperature, humidity, rainfall estimates, and wind conditions via Open-Meteo with zero required API keys and graceful fallback.
- **Agronomic Multi-Crop Matching**: Random Forest Classifier matching N-P-K nutrient profiles, soil pH, and moisture against vetted agronomic baselines.
- **Multi-Year Scenario Forecasting (2027–2031)**: Horizon-specific models with empirical error bands under Normal, Drier, and Wetter weather scenarios.
- **Persistent Audit Logging**: SQLite database recording every prediction with timestamp, selected model version, district, and predicted yield.

---

## 5. Technology Stack

### Backend
- **Framework**: FastAPI 0.110+, Uvicorn 0.28+ (ASGI asynchronous server)
- **Data & ML**: Scikit-Learn 1.4+, NumPy 1.26+, Pandas 2.2+, Joblib 1.3+
- **Validation**: Pydantic v2
- **Explainability**: SHAP 0.45+ (TreeExplainer & Closed-form Linear Waterfall)
- **Database**: SQLite (SQLAlchemy / Python sqlite3)
- **Testing**: Pytest 9.1+, AnyIO

### Frontend
- **Library**: React 18
- **Build Tool**: Vite 8.2
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios

---

## 6. Empirical Model Evaluation Summary

All models were evaluated on the exact same 13 expanding chronological folds (2011–2023, 6 target districts, $N=78$ out-of-fold test observations):

| Model Version | Architecture | Feats | CV MAE (kg/ha) | CV RMSE (kg/ha) | CV WAPE (%) | CV $R^2$ | Signed Bias (kg/ha) | Fold Error Std (kg/ha) | 2024 Checkpoint MAE* (kg/ha) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Thermal-Only Ridge** (`candidate_six_district_thermal`) | RobustScaler + Ridge ($\alpha=100$) on 3yr rolling delta | 38 | **104.75** | **138.10** | **32.28%** | **0.2305** | -24.66 | **56.91** | 119.84 |
| **Physiological Ridge** (`candidate_six_district_physiological`) | RobustScaler + Ridge ($\alpha=100$) on 3yr rolling delta | 45 | 106.11 | 140.76 | 32.70% | 0.2006 | -25.37 | 58.45 | 116.43 |
| **Retrained Gradient Boosting** (Expanding Window) | Standard GradientBoostingRegressor ($n=100, d=3, \eta=0.05$) | 36 | 116.42 | 151.65 | 35.87% | 0.0722 | -31.60 | 73.10 | 129.70 |
| **Baseline: Previous-Year Persistence** | Naive lag-1 persistence ($\hat{y}_t = y_{t-1}$) | 1 | 127.71 | 176.05 | 39.35% | -0.2503 | -21.87 | 84.02 | 109.27 |
| *Saved Production GB (In-Sample Baseline)* | Production artifact evaluated in-sample on train panel | 36 | *30.08* | *40.06* | *9.27%* | *0.9353* | *-6.56* | *10.13* | 139.62 |

*\*Note 1: 2024 results reflect an inspected sanity checkpoint, not an untouched blind holdout.*
*\*Note 2 (Evaluation Discrepancy Reconciliation): The historical 111.8 kg/ha MAE reported in earlier documentation was evaluated over all 7 Vidarbha districts ($N=91$ observations across 13 folds). When evaluated strictly on the 6 target districts under identical chronological folds ($N=78$ observations), retrained Gradient Boosting yields 116.42 kg/ha, demonstrating an authentic 11.67 kg/ha error reduction by Thermal Ridge (104.75 kg/ha).*

### District-Level Cross-Validation MAE (kg/ha)
- **Akola**: Thermal 69.39 vs Physio 72.64 (+3.25 advantage)
- **Amravati**: Thermal 161.47 vs Physio 162.51 (+1.03 advantage) — highest regional volatility
- **Buldhana**: Thermal 128.38 vs Physio 129.62 (+1.24 advantage)
- **Nagpur**: Thermal 70.46 vs Physio 73.30 (+2.84 advantage)
- **Wardha**: Thermal 104.75 vs Physio 105.27 (+0.52 advantage)
- **Washim**: Thermal 94.04 vs Physio 93.32 (-0.72 deficit)

---

## 7. Installation and Setup Guide

### Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13
- **Node.js**: Version 18.x or 20.x
- **Package Manager**: npm or yarn

### 1. Clone & Navigate to Repository
```bash
git clone https://github.com/<your-username>/AgriPredict-AI.git
cd AgriPredict-AI
```

### 2. Backend Setup
Create a virtual environment and install backend dependencies:
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

*(Optional)* Create a `.env` file in the root or `backend/` directory if configuring custom weather credentials:
```env
WEATHER_API_KEY=demo_weather_key
PORT=8000
```
*(Note: If `WEATHER_API_KEY` is not provided or set to `demo_weather_key`, the service automatically routes to free Open-Meteo live data).*

### 3. Frontend Setup
Install frontend npm packages:
```bash
cd frontend
npm install
cd ..
```

---

## 8. Running the Application

### Start the Backend Server
```bash
# From project root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Redoc Documentation: `http://127.0.0.1:8000/redoc`

### Start the Frontend Server
```bash
# In a new terminal window:
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- Web Application UI: `http://127.0.0.1:5173`

---

## 9. Testing and Verification

Run the complete backend test suite (109 automated tests):
```bash
# Run pytest from project root
python -m pytest backend/tests/ -v
```
Expected output:
```
====================== 109 passed, 34 warnings in ~7s =======================
```

Run the frontend production build:
```bash
cd frontend
npm run build
```
Expected output:
```
✓ 2486 modules transformed.
dist/index.html                   0.45 kB
dist/assets/index-*.css          85.39 kB
dist/assets/index-*.js          837.43 kB
✓ built in ~600ms
```

---

## 10. API Route Reference

| Method | Endpoint | Description | Sample Request Body |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/cotton/predict` | Predict cotton yield with XAI attribution | `{"district": "Akola", "target_year": 2024, "model_version": "candidate_six_district_thermal"}` |
| `POST` | `/api/yield/predict` | Multi-crop yield estimation | `{"district": "Pune", "crop": "Tomato", "area_ha": 2.5, "rainfall_mm": 600, ...}` |
| `POST` | `/api/crop/recommend` | Crop suitability ranking | `{"district": "Nashik", "soil_nitrogen": 90, "soil_ph": 6.5, ...}` |
| `GET` | `/api/weather/{district}` | Real-time weather info | *URL parameter: district name* |
| `GET` | `/api/cotton/future-forecast` | Multi-year forecast (2027–2031) | *Query parameter: district* |
| `GET` | `/api/history` | Historical prediction logs | *None* |

---

## 11. Important Interpretation & Limitations

1. **Post-Monsoon Forecast Timing**: The model relies on realized in-season Kharif agro-meteorological observations accumulated through October 31 (cumulative Kharif precipitation, rainy days, and peak temperature indices). Predictions represent **post-monsoon pre-harvest estimates (October/November)**, not pre-sowing planting recommendations.
2. **Empirically Calibrated Out-of-Fold Error Bounds ($\pm 253.5\text{ kg/ha}$)**:
   - The default error interval ($\pm 253.5\text{ kg/ha}$) represents **Empirically Calibrated Out-of-Fold Error Bounds (Retrospective 2011–2023)**, NOT a theoretical Gaussian or distribution-free guaranteed 90% confidence interval.
   - **Retrospective Circularity**: The 92.3% historical coverage reported across the 78 out-of-fold residuals (2011–2023) is mathematically circular: the $253.5\text{ kg/ha}$ threshold is by definition the 72nd order statistic out of 78 ($k = \lceil 79 \times 0.90 \rceil = 72$), so $72 / 78 = 92.307\%$ is a descriptive tautology.
   - **Strict Rolling-Origin Prequential Calibration**: When evaluated strictly prospectively (using only years $< t$ to calibrate threshold for year $t$):
     - Years 2011 & 2012 cannot be calibrated prospectively due to sample size constraints ($N=0$ and $N=6 < 10$, where $k = \lceil 7 \times 0.90 \rceil = 7 > 6$).
     - Over all eligible forecast years (2013–2023, $N=66$), strict rolling-origin calibration achieved **87.9% empirical coverage**.
     - During the 2016 bumper post-drought recovery year, prequential coverage collapsed to **16.7%** (5 out of 6 districts breached the bound) because previous drought years (2014 & 2015) artificially contracted the threshold to $205.4\text{ kg/ha}$.
   - **Independent 2024 Holdout**: Covered 6 out of 6 districts ($100.0\%$), but $N=6$ is statistically insufficient to prove long-term guarantees.
   - **Asymmetric Calibration Geometry**: The signed error distribution ($y - \hat{y}$) has a heavy positive tail (underpredictions up to $+433.6\text{ kg/ha}$) and a truncated negative tail ($-281.9\text{ kg/ha}$). Asymmetric bounds ($[-156.5, +258.1]\text{ kg/ha}$) yield a total width of $414.6\text{ kg/ha}$ ($156.5 + 258.1$), achieving a **$92.4\text{ kg/ha}$ reduction in width** compared to the symmetric span of $507.0\text{ kg/ha}$ ($2 \times 253.5$) while preserving 89.7% empirical coverage.
3. **District & High-Yield Regimes**:
   - **Amravati Variance**: Higher historical yield variance causes coverage in Amravati to drop to 76.9% under the retrospective bound.
   - **High-Yield Under-Prediction**: In bumper harvests ($>450\text{ kg/ha}$ or $>500\text{ kg/ha}$), regression models systematically underpredict yields, increasing upper-bound breach rates up to 27.8%.
4. **WAPE Error Metric**: A WAPE of 32.28% is a scale-independent error metric ($\sum |y - \hat{y}| / \sum y$), not an accuracy percentage. It must not be cited as "67.72% accuracy".
5. **Future Weather Scenarios**: Projections for 2027–2031 reflect controlled synthetic scenarios (Normal, Dry, Wet) and should be used for stress-testing rather than meteorological forecasting.

---

## 12. Project Structure

```
AgriPredict-AI/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── config.py                   # System configuration & crop baselines
│   ├── database/                   # SQLite database engine & schema
│   ├── ml/
│   │   ├── artifacts/              # Production model artifacts (final_model.pkl)
│   │   ├── cotton_predictor.py     # Cotton inference & multi-model router
│   │   ├── experiments/            # Optimization workflows & candidate artifacts
│   │   └── models/                 # Crop suitability & yield classifiers
│   ├── routes/                     # FastAPI route controllers
│   ├── services/                   # Input feature builders & weather service
│   └── tests/                      # 109 automated regression & unit tests
├── data/
│   ├── vidarbha_cotton_model_ready_1997_2024.csv # Canonical panel dataset
│   └── raw/                        # Baseline agricultural datasets
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI components (Navbar, Footer, Cards)
│   │   ├── constants/              # Shared six-district authority (districts.js)
│   │   ├── pages/                  # Page views (Dashboard, CottonYield, Weather, etc.)
│   │   └── App.jsx                 # Client-side routing & theme setup
│   ├── package.json
│   └── vite.config.js
├── reports/
│   └── FINAL_MODEL_EVALUATION_AND_PROJECT_READINESS_REPORT.md # Technical report
└── README.md                       # Master project documentation
```

---

## 13. License & Academic Disclaimer

This project was built for academic research and engineering demonstration purposes. Model predictions represent statistical estimates and should not be used as the sole basis for high-stakes financial or commercial agricultural decisions.
