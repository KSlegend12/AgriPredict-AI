# AgriPredictAI Review-Ready Frontend

This package is a UI-focused replacement for the existing frontend. It preserves the existing backend/API service layer and the existing prediction/history/weather/future-forecast pages.

## Replace

Copy the contents of this `frontend` folder over the project's existing `frontend` folder.

Important files redesigned:
- `src/App.jsx`
- `src/index.css`
- `src/App.css`
- `src/components/Navbar.jsx`
- `src/components/Footer.jsx`
- `src/pages/LandingPage.jsx`
- `src/pages/Dashboard.jsx`
- `src/pages/ModelInsightsPage.jsx`
- `src/pages/SatelliteDataPage.jsx`
- `src/pages/HowItWorksPage.jsx`
- `src/pages/AboutPage.jsx`

New routes:
- `/satellite`
- `/how-it-works`

Existing routes are retained:
- `/`
- `/dashboard`
- `/cotton`
- `/yield`
- `/future-forecast`
- `/insights`
- `/weather`
- `/history`
- `/recommend`
- `/about`

## Important

The current production model is GradientBoostingRegressor, not Random Forest. The redesigned UI uses the authoritative project metrics:
- Validation (2011–2023): MAE 106.1784, RMSE 126.6537, R² -1.5769, MAPE 38.1557%
- 2024 holdout: MAE 230.7527, RMSE 321.4472, R² -0.6360, MAPE 41.6921%
- 2024 previous-year baseline MAE: 189.8643 kg/ha
- 2024 historical-mean baseline MAE: 281.183 kg/ha

The satellite page intentionally distinguishes extraction availability from model performance. A dataset being complete does not imply that it improves the production model.

## Run

From the frontend folder:

```powershell
npm install
npm run dev
```

If `node_modules` came from another OS, delete `node_modules` and run `npm install` before `npm run dev`.
