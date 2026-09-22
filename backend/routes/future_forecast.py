from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.ml.future_forecasting.predictor import (
    DISTRICTS,
    SCENARIOS,
    forecast_all,
    forecast_district,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/cotton/future-forecast",
    tags=["Cotton Future Forecast"],
)


# =========================================================
# EXISTING 2027–2031 FORECAST ROUTES
# =========================================================

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
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# NEW 2026 EXPERIMENTAL SCENARIO PREDICTION
# =========================================================

@router.get("/2026/{district}")
def experimental_2026_forecast(district: str):
    """
    Return the already-generated 2026 experimental
    Dry / Normal / Wet scenario predictions.

    IMPORTANT:
    - This endpoint does NOT retrain the production model.
    - It does NOT generate a new prediction.
    - It only serves the verified experimental CSV.
    - Actual 2026 yield is not available.
    """

    try:
        # -------------------------------------------------
        # Experimental prediction file
        # -------------------------------------------------

        prediction_path = Path(
            "data/cotton_2026_experimental_predictions.csv"
        )

        if not prediction_path.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    "2026 experimental prediction file not found: "
                    "data/cotton_2026_experimental_predictions.csv"
                ),
            )

        # -------------------------------------------------
        # Load predictions
        # -------------------------------------------------

        df = pd.read_csv(prediction_path)

        # -------------------------------------------------
        # Validate required columns
        # -------------------------------------------------

        required_columns = [
            "district",
            "target_year",
            "scenario",
            "predicted_yield_kg_ha",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "2026 prediction file has missing columns.",
                    "missing_columns": missing_columns,
                },
            )

        # -------------------------------------------------
        # Find requested district
        # -------------------------------------------------

        district_rows = df[
            df["district"].astype(str).str.lower()
            == district.lower()
        ].copy()

        if district_rows.empty:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown district: {district}",
            )

        # -------------------------------------------------
        # Sort scenarios consistently
        # -------------------------------------------------

        scenario_order = {
            "dry": 0,
            "normal": 1,
            "wet": 2,
        }

        district_rows["_scenario_order"] = (
            district_rows["scenario"]
            .astype(str)
            .str.lower()
            .map(scenario_order)
            .fillna(99)
        )

        district_rows = district_rows.sort_values(
            "_scenario_order"
        )

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------

        scenarios = []

        for _, row in district_rows.iterrows():
            scenarios.append(
                {
                    "scenario": str(row["scenario"]),
                    "predicted_yield_kg_ha": round(
                        float(row["predicted_yield_kg_ha"]),
                        2,
                    ),
                }
            )

        return {
            "target_year": 2026,
            "district": str(
                district_rows.iloc[0]["district"]
            ),
            "prediction_type": (
                "scenario_based_experimental_prediction"
            ),
            "actual_target_available": False,
            "source": (
                "data/"
                "cotton_2026_experimental_predictions.csv"
            ),
            "scenarios": scenarios,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# =========================================================
# EXISTING DISTRICT FORECAST ROUTE
# =========================================================

@router.get("/{district}")
def future_forecast(district: str):
    """
    Existing 2027–2031 future forecast.
    Keep this separate from the 2026 experimental endpoint.
    """

    try:
        return forecast_district(district)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )