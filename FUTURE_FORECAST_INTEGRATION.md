# Future Cotton Yield Forecasting — 2027–2031

Integrated into AgriPredict-AI as a separate module.

## New backend
- `backend/ml/future_forecasting/predictor.py`
- `backend/ml/future_forecasting/__init__.py`
- Existing `future_horizon_models.joblib` retained
- `backend/routes/future_forecast.py`

API:
- `GET /api/cotton/future-forecast/districts`
- `GET /api/cotton/future-forecast/all`
- `GET /api/cotton/future-forecast/{district}`

## New frontend
- `frontend/src/pages/FutureCottonForecastPage.jsx`
- API helpers added to `frontend/src/services/api.js`
- `/future-forecast` route added to `frontend/src/App.jsx`
- `5-Year Forecast` navigation link added to Navbar

## Safety
The existing validated 2024 cotton model and authoritative dataset were not retrained or changed.

2027–2031 forecasts use explicit Normal/Dry/Wet weather scenarios. They are future model estimates, not verified observations.
