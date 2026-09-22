# \# AgriPredict-AI

# 

# > AI/ML Decision-Support System for Agricultural Analysis and Cotton Yield Forecasting in Maharashtra

# 

# AgriPredict-AI is an AI/ML-based agricultural decision-support system for Maharashtra, India. The application combines existing agricultural decision-support modules with a dedicated machine-learning workflow for cotton yield prediction and future cotton-yield forecasting in seven Vidarbha districts.

# 

# The project includes historical agricultural data, weather-related features, chronological machine-learning validation, future scenario forecasting, empirical uncertainty bands, and an experimental satellite soil-moisture workflow.

# 

# \---

# 

# \## 1. Project Overview

# 

# AgriPredict-AI currently contains two major application areas.

# 

# \### A. Agricultural Decision-Support Modules

# 

# The application includes existing modules for:

# 

# \- District information

# \- Weather information

# \- Crop suitability

# \- Agricultural yield prediction

# \- Prediction/history records

# 

# The existing crop-suitability module supports:

# 

# 1\. Tomato

# 2\. Onion

# 3\. Sugarcane

# 

# These modules are retained as part of the application and are separate from the dedicated Vidarbha cotton forecasting workflow.

# 

# \### B. Vidarbha Cotton Yield Prediction

# 

# The main validated ML workflow focuses on cotton yield prediction for seven Vidarbha districts:

# 

# 1\. Akola

# 2\. Amravati

# 3\. Buldhana

# 4\. Nagpur

# 5\. Wardha

# 6\. Washim

# 7\. Yavatmal

# 

# The authoritative historical cotton dataset covers harvest years \*\*1997–2024\*\*.

# 

# The production model is trained using \*\*1997–2023\*\* data, while \*\*2024 is retained as an untouched final holdout year\*\*.

# 

# \---

# 

# \# 2. Cotton Yield Prediction Dataset

# 

# Authoritative dataset:

# 

# ```text

# backend/data/vidarbha\_cotton\_model\_ready\_1997\_2024.csv

# 

# Dataset characteristics:

# 

# Property	Value

# Total observations	194

# Total columns	43

# Historical years	1997–2024

# Training years	1997–2023

# Training observations	187

# Final holdout year	2024

# Districts	7

# Target column	yield\_target\_kg\_ha

# 

# The target variable represents cotton yield in kg/ha.

# 

# The 2024 target values are kept outside the training data and are used only for final holdout evaluation.

# 

# 3\. Supported Cotton Districts

# 

# The cotton prediction workflow supports the following seven Vidarbha districts:

# 

# District

# Akola

# Amravati

# Buldhana

# Nagpur

# Wardha

# Washim

# Yavatmal

# 

# Yavatmal is retained as part of the authoritative dataset and model evaluation.

# 

# 4\. Production Cotton Model

# 

# The validated production cotton model is:

# 

# GradientBoostingRegressor

# 

# Current hyperparameters:

# 

# n\_estimators = 100

# learning\_rate = 0.05

# max\_depth = 3

# random\_state = 42

# 

# The production model is kept separate from experimental satellite modelling and the separate future-forecasting model artifacts.

# 

# 5\. Temporal Validation

# 

# Agricultural yield is time-dependent. Therefore, the cotton workflow uses chronological validation rather than a random train/test split.

# 

# The validation strategy uses an expanding-window chronological / rolling-origin approach.

# 

# Validation period:

# 

# 2011–2023

# 

# Final holdout:

# 

# 2024

# 

# The 2024 target values remain an untouched final holdout during model training.

# 

# This approach is intended to reduce temporal leakage and provide a more realistic historical evaluation.

# 

# 6\. Production Model Evaluation

# 2024 Final Holdout

# 

# The final 2024 holdout metrics are:

# 

# Metric	Value

# MAE	230.7527 kg/ha

# RMSE	321.4472 kg/ha

# R²	-0.636

# MAPE	41.6921%

# Baseline Comparison

# 

# The project preserves simple baseline models for comparison.

# 

# Baseline	2024 MAE

# Previous-year yield	189.8643 kg/ha

# Historical mean	281.1830 kg/ha

# 

# These baselines remain part of the evaluation and are not removed when comparing the machine-learning model.

# 

# Important: R² is a regression evaluation metric. It is not described as prediction accuracy.

# 

# 7\. Future Cotton Yield Forecasting

# 

# The project contains a separate future-forecasting module:

# 

# backend/ml/future\_forecasting/

# 

# The module generates cotton-yield forecasts for:

# 

# 2027

# 2028

# 2029

# 2030

# 2031

# 

# The forecast origin is:

# 

# 2024

# 

# The system uses direct horizon-specific models.

# 

# Forecast Year	Forecast Horizon

# 2027	3 years

# 2028	4 years

# 2029	5 years

# 2030	6 years

# 2031	7 years

# 

# Future target yield values are not used as future input features.

# 

# 8\. Future Forecast Model Selection

# 

# The saved future-forecasting artifacts use horizon-specific model selection:

# 

# Horizon	Selected Model

# 1	Ridge

# 2	RandomForest

# 3	RandomForest

# 4	RandomForest

# 5	RandomForest

# 6	GradientBoosting

# 7	RandomForest

# 

# Therefore, the currently generated 2027–2031 forecasts use:

# 

# Forecast Year	Horizon	Model

# 2027	3	RandomForest

# 2028	4	RandomForest

# 2029	5	RandomForest

# 2030	6	GradientBoosting

# 2031	7	RandomForest

# 

# These future-forecasting model artifacts are separate from the validated production cotton model.

# 

# 9\. Future Weather Scenarios

# 

# Future weather conditions are unknown. Therefore, the future forecasting module provides three controlled scenarios.

# 

# Normal

# 

# Uses recent historical district weather climatology.

# 

# Dry

# 

# Represents a controlled drier-weather scenario using changes such as:

# 

# Reduced rainfall

# Reduced rain-day counts

# Reduced heavy-event measures

# Increased dry-spell characteristics

# Wet

# 

# Represents a controlled wetter-weather scenario using changes such as:

# 

# Increased rainfall

# Increased rain-day counts

# Increased heavy-event measures

# Reduced dry-spell characteristics

# 

# These are modelling scenarios and should not be interpreted as actual weather forecasts.

# 

# 10\. Forecast Uncertainty

# 

# The future forecast interface provides empirical uncertainty bands around point predictions.

# 

# The uncertainty calibration is based on historical out-of-sample prediction errors.

# 

# Calibration period:

# 

# 2015–2020

# 

# Evaluation period:

# 

# 2021–2024

# 

# Calibration quantile:

# 

# 90th percentile absolute prediction error

# 

# Current horizon-specific empirical error bands:

# 

# Horizon	Empirical Error Band

# 1	276.30 kg/ha

# 2	262.05 kg/ha

# 3	270.35 kg/ha

# 4	280.12 kg/ha

# 5	278.85 kg/ha

# 6	345.27 kg/ha

# 7	295.62 kg/ha

# 

# The forecast interface displays:

# 

# Predicted yield

# Empirical lower bound

# Empirical upper bound

# Empirical uncertainty band

# Forecast horizon

# Selected model

# 

# The uncertainty bands are historical empirical error bands.

# 

# They are not guaranteed future confidence intervals.

# 

# 11\. Satellite / SMAP Experimental Workflow

# 

# The project also contains an experimental satellite-data workflow using NASA SMAP soil-moisture data.

# 

# Product:

# 

# SPL4SMGP.008

# 

# The workflow extracts surface and root-zone soil-moisture features.

# 

# Coverage:

# 

# 2017–2024

# 

# The experiment covers all seven supported Vidarbha districts.

# 

# The satellite workflow follows:

# 

# Satellite Data

# &#x20;     ↓

# District-Year Feature Extraction

# &#x20;     ↓

# Quality Assurance

# &#x20;     ↓

# Forecast-Origin-Safe Merge

# &#x20;     ↓

# Controlled Hindcast

# &#x20;     ↓

# Baseline Comparison

# 

# The extracted SMAP feature dataset contains:

# 

# 56 rows

# 7 districts × 8 years

# 

# The SMAP feature workflow passed its district-year completeness and quality checks.

# 

# 12\. SMAP Controlled Experiment

# 

# The SMAP workflow is an experimental research component.

# 

# The controlled experiment compares:

# 

# BASE

# 

# against:

# 

# BASE + SMAP

# 

# using the same forecast-origin-safe evaluation framework.

# 

# Selected results:

# 

# Model	Horizon	BASE MAE	SMAP MAE	Change

# GradientBoosting	1	182.20	170.48	-6.43%

# GradientBoosting	2	206.68	199.59	-3.43%

# RandomForest	1	164.90	156.46	-5.12%

# RandomForest	2	185.76	185.58	-0.09%

# Ridge	1	179.71	151.94	-15.45%

# Ridge	2	247.49	277.95	+12.31%

# 

# Because SMAP coverage is limited to 2017–2024, only horizons with sufficient training observations were evaluated.

# 

# The experiment provides promising but limited evidence regarding the usefulness of satellite soil-moisture features.

# 

# Production Status

# 

# SMAP features are currently experimental.

# 

# They have not been automatically integrated into the production cotton model.

# 

# The production model and authoritative historical dataset remain unchanged.

# 

# 13\. Project Architecture

# AgriPredict-AI/

# │

# ├── backend/

# │   ├── main.py

# │   ├── config.py

# │   │

# │   ├── routes/

# │   │   ├── districts.py

# │   │   ├── weather.py

# │   │   ├── crop.py

# │   │   ├── yield\_predict.py

# │   │   ├── history.py

# │   │   ├── cotton.py

# │   │   └── future\_forecast.py

# │   │

# │   ├── schemas/

# │   │   └── request\_schemas.py

# │   │

# │   ├── services/

# │   │   └── cotton\_input\_builder.py

# │   │

# │   ├── ml/

# │   │   ├── predictor.py

# │   │   ├── cotton\_predictor.py

# │   │   │

# │   │   ├── evaluation/

# │   │   │   ├── MODEL\_VALIDATION\_REPORT.md

# │   │   │   ├── MODEL\_DIAGNOSTIC\_REPORT.md

# │   │   │   └── final/

# │   │   │

# │   │   └── future\_forecasting/

# │   │       ├── predictor.py

# │   │       ├── artifacts/

# │   │       ├── outputs/

# │   │       └── data\_audit/

# │   │

# │   ├── data/

# │   │   └── vidarbha\_cotton\_model\_ready\_1997\_2024.csv

# │   │

# │   └── requirements.txt

# │

# ├── frontend/

# │   ├── src/

# │   │   ├── components/

# │   │   ├── pages/

# │   │   └── services/

# │   │

# │   ├── package.json

# │   └── vite.config.js

# │

# ├── FUTURE\_FORECAST\_INTEGRATION.md

# ├── PROJECT\_STATUS.md

# └── README.md

# 14\. Backend Technology Stack

# 

# The backend uses:

# 

# Python

# FastAPI

# Pydantic

# Scikit-learn

# XGBoost

# SHAP

# Pandas

# NumPy

# Joblib

# HTTPX

# Python-dotenv

# Uvicorn

# 

# Backend dependencies are specified in:

# 

# backend/requirements.txt

# 15\. Frontend Technology Stack

# 

# The frontend uses:

# 

# React

# Vite

# Tailwind CSS

# Lucide Icons

# Recharts

# Axios

# React Router

# 

# The frontend provides the application dashboard and future cotton forecasting interface.

# 

# 16\. API Endpoints

# General Health

# GET /

# GET /api/health

# 

# Returns application status and model metadata.

# 

# District Information

# GET /api/districts

# 

# Provides district information for the agricultural application.

# 

# Weather

# GET /api/weather/{district}

# 

# Provides weather information for the requested district.

# 

# Crop Suitability

# POST /api/crop/recommend

# 

# Runs the existing crop-suitability workflow.

# 

# Agricultural Yield Prediction

# POST /api/yield/predict

# 

# Runs the existing agricultural yield-prediction workflow.

# 

# History

# GET /api/history

# 

# Returns application prediction/search history where supported.

# 

# 17\. Cotton Yield API

# 

# Base endpoint:

# 

# /api/cotton

# Predict Cotton Yield

# POST /api/cotton/predict

# 

# Builds the required model feature row from verified historical data and returns a cotton-yield prediction.

# 

# The response also identifies whether the requested year is the 2024 historical holdout evaluation year or another historical model-estimate year.

# 

# Get Prediction Input

# GET /api/cotton/input/{district}/{year}

# 

# Returns the verified model inputs used for a district/year prediction.

# 

# Get Cotton Weather

# GET /api/cotton/weather/{district}/{year}

# 

# Returns the weather summary associated with the specified cotton district and year.

# 

# Get Cotton History

# GET /api/cotton/history/{district}

# 

# Returns historical cotton information for the requested district.

# 

# List Cotton Districts

# GET /api/cotton/districts

# 

# Returns the supported Vidarbha cotton districts and available prediction years.

# 

# Supported districts:

# 

# Akola

# Amravati

# Buldhana

# Nagpur

# Wardha

# Washim

# Yavatmal

# Cotton Model Information

# GET /api/cotton/model/info

# 

# Returns:

# 

# Model name

# Crop

# Geographic scope

# Training period

# Number of training observations

# Temporal validation strategy

# Validation metrics

# 2024 holdout metrics

# Number of model features

# Feature columns

# Top feature importances

# Model comparison information

# Supported prediction years

# Model loading status

# 18\. Future Cotton Forecast API

# 

# Base endpoint:

# 

# /api/cotton/future-forecast

# Forecast District List

# GET /api/cotton/future-forecast/districts

# 

# Returns the districts supported by the future forecasting module.

# 

# Forecast All Districts

# GET /api/cotton/future-forecast/all

# 

# Returns future cotton forecasts for all supported districts.

# 

# Forecast Individual District

# GET /api/cotton/future-forecast/{district}

# 

# Returns future cotton forecasts for an individual district.

# 

# Forecast years:

# 

# 2027

# 2028

# 2029

# 2030

# 2031

# 

# The response includes:

# 

# Predicted yield

# Empirical lower bound

# Empirical upper bound

# Empirical uncertainty band

# Forecast horizon

# Selected model

# Weather scenario information

# 19\. Running the Backend

# 

# From the project root:

# 

# python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 

# The backend will be available at:

# 

# http://127.0.0.1:8000

# 

# Health endpoint:

# 

# http://127.0.0.1:8000/api/health

# 

# Interactive FastAPI documentation:

# 

# http://127.0.0.1:8000/docs

# 

# The normal startup command does not retrain the production ML model.

# 

# 20\. Running the Frontend

# 

# Open another terminal:

# 

# cd frontend

# npm install

# npm run dev

# 

# The Vite development server will display the frontend URL in the terminal.

# 

# The frontend normally runs at:

# 

# http://127.0.0.1:5173

# 

# The frontend communicates with the FastAPI backend through the configured API URL.

# 

# 21\. Production Frontend Build

# 

# To create a production frontend build:

# 

# cd frontend

# npm run build

# 

# The generated production files are placed in:

# 

# frontend/dist/

# 

# The build should complete without compilation errors before release.

# 

# 22\. Validation and Audit Documentation

# 

# Important model-validation documentation is located in:

# 

# backend/ml/evaluation/

# 

# Important files include:

# 

# MODEL\_VALIDATION\_REPORT.md

# MODEL\_DIAGNOSTIC\_REPORT.md

# final/FINAL\_MODEL\_VALIDATION\_REPORT.md

# 

# Future-forecasting audit documentation is located in:

# 

# backend/ml/future\_forecasting/data\_audit/

# 

# Important files include:

# 

# DATA\_AUDIT\_GATE.md

# future\_forecast\_audit.md

# STRICT\_FORECAST\_ORIGIN\_AUDIT.md

# 

# Project-level documentation includes:

# 

# PROJECT\_STATUS.md

# FUTURE\_FORECAST\_INTEGRATION.md

# 

# These documents contain detailed information about validation, data auditing, forecasting methodology, model selection, and implementation status.

# 

# 23\. Reproducibility and Data-Safety Rules

# 

# The project follows these principles:

# 

# The authoritative historical cotton dataset must not be modified casually.

# The 2024 target values must remain isolated from model training.

# Future target yield values must never be used as future input features.

# Yavatmal must remain part of the supported district set.

# Previous-year and historical-mean baselines must remain available for comparison.

# Experimental satellite features must not automatically replace the production model.

# R² must not be described as prediction accuracy.

# Historical hindcast performance must not be presented as a guarantee of future performance.

# Empirical uncertainty bands must not be described as guaranteed confidence intervals.

# Changes to the production model should be explicitly evaluated before adoption.

# Future forecasting artifacts should remain separate from the validated historical production model.

# Experimental results should be clearly distinguished from production results.

# 24\. Current Project Status

# 

# The current system includes:

# 

# Maharashtra agricultural decision-support modules

# Crop suitability functionality

# Weather functionality

# Agricultural yield prediction functionality

# Vidarbha cotton yield prediction

# Seven-district cotton coverage

# Historical cotton data from 1997–2024

# 1997–2023 cotton model training

# 2024 untouched final holdout

# Chronological expanding-window validation

# Previous-year baseline

# Historical-mean baseline

# 2027–2031 future cotton forecasting

# Horizon-specific future models

# Normal/Dry/Wet weather scenarios

# Empirical forecast uncertainty bands

# SMAP satellite-data experiment

# Forecast-origin leakage audits

# FastAPI backend

# React/Vite frontend

# Forecast visualization

# Forecast uncertainty visualization

# API documentation through FastAPI/OpenAPI

# 

# The SMAP satellite workflow remains experimental and is intentionally separated from the production cotton model.

# 

# 25\. Important Interpretation Notes

# Historical Model

# 

# The 2024 holdout evaluation represents performance on a specific historical year and should not be interpreted as a guarantee of future performance.

# 

# Future Forecast

# 

# The 2027–2031 forecasts depend on historical patterns, engineered features, model assumptions, and future-weather scenarios.

# 

# Weather Scenarios

# 

# Normal, Dry, and Wet are scenario definitions rather than actual meteorological forecasts.

# 

# Uncertainty Bands

# 

# The displayed forecast ranges are empirical historical error bands. They should not be interpreted as guaranteed future confidence intervals.

# 

# Satellite Features

# 

# The SMAP workflow is experimental and has not been promoted into the production model.

# 

# 26\. Disclaimer

# 

# AgriPredict-AI is an academic and engineering AI/ML decision-support project.

# 

# Model outputs are estimates based on historical data, engineered features, modelling assumptions, and scenario definitions.

# 

# The system should not be interpreted as providing guaranteed agricultural outcomes or as a replacement for professional agronomic advice.

# 

# Future scenario forecasts are particularly sensitive to assumptions about future weather and other changing conditions.

# 

# 27\. License and Credits

# 

# Built as an academic/engineering AI/ML project for agricultural decision-support research and demonstration.

# 

# AgriPredict-AI combines machine learning, agricultural data analysis, temporal validation, forecasting, and web-based visualization into a single decision-support application.

