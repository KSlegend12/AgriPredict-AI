from fastapi import APIRouter, HTTPException

from backend.ml.future_forecasting.predictor import (
    DISTRICTS,
    SCENARIOS,
    forecast_all,
    forecast_district,
)

router = APIRouter(prefix="/api/cotton/future-forecast", tags=["Cotton Future Forecast"])

@router.get("/districts")
def future_forecast_districts():
    return {
        "districts": DISTRICTS,
        "forecast_years": [2027, 2028, 2029, 2030, 2031],
        "scenarios": list(SCENARIOS),
    }

@router.get("/all")
def future_forecast_all():
    try:
        return {
            "origin_year": 2024,
            "forecast_years": [2027, 2028, 2029, 2030, 2031],
            "data": forecast_all(),
        }
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/{district}")
def future_forecast(district: str):
    try:
        return forecast_district(district)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
