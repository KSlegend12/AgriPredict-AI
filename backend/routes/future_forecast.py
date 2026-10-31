from pathlib import Path
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.ml.future_forecasting.predictor import (
    DISTRICTS,
    SCENARIOS,
    forecast_all,
    forecast_district,
)

logger = logging.getLogger("agripredict.future_forecast")


# =========================================================
# PATH RESOLUTION (anchored to __file__, not CWD)
# =========================================================

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]

RESULTS_2025_DIR = _REPO_ROOT / "backend" / "ml" / "evaluation" / "experimental_2025_train_to_2024"
DISTRICT_RESULTS_2025_PATH = RESULTS_2025_DIR / "2025_out_of_sample_district_results.csv"
METRICS_2025_PATH = RESULTS_2025_DIR / "2025_out_of_sample_model_comparison.csv"
PREDICTIONS_2026_PATH = _REPO_ROOT / "data" / "cotton_2026_experimental_predictions.csv"


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/cotton/future-forecast",
    tags=["Cotton Future Forecast"],
)


# =========================================================
# EXISTING 2027-2031 FORECAST ROUTES
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

    except FileNotFoundError as exc:
        logger.error("Future forecast artifact missing: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Future forecast model artifacts are not available.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        logger.error("Future forecast all error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating future forecasts.",
        )


# =========================================================
# 2025 EXPERIMENTAL OUT-OF-SAMPLE EVALUATION
# =========================================================

@router.get("/2025/{district}")
def experimental_2025_forecast(district: str):
    """
    Return the verified 2025 experimental RandomForest
    out-of-sample prediction and actual benchmark.

    IMPORTANT:
    - This endpoint does NOT retrain the production model.
    - It does NOT modify the production GradientBoosting model.
    - It only serves the verified 2025 experimental results.
    - Training: 1997-2024
    - Test: 2025
    - Model: RandomForest
    - 2025 weather is observed/end-of-season weather.
    """

    try:
        # -------------------------------------------------
        # Experimental 2025 district results
        # -------------------------------------------------

        district_results_path = DISTRICT_RESULTS_2025_PATH

        if not district_results_path.exists():
            raise HTTPException(
                status_code=404,
                detail="2025 experimental district results are not available.",
            )

        # -------------------------------------------------
        # Overall model comparison metrics
        # -------------------------------------------------

        metrics_path = METRICS_2025_PATH

        if not metrics_path.exists():
            raise HTTPException(
                status_code=404,
                detail="2025 experimental model comparison metrics are not available.",
            )

        # -------------------------------------------------
        # Load files
        # -------------------------------------------------

        df = pd.read_csv(district_results_path)
        metrics_df = pd.read_csv(metrics_path)

        # -------------------------------------------------
        # Validate district result columns
        # -------------------------------------------------

        required_columns = [
            "model",
            "district",
            "actual_2025_kg_ha",
            "predicted_2025_kg_ha",
            "error_kg_ha",
            "abs_error_kg_ha",
            "pct_error",
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
                    "message": (
                        "2025 experimental district results "
                        "file has missing columns."
                    ),
                    "missing_columns": missing_columns,
                },
            )

        # -------------------------------------------------
        # Validate metrics columns
        # -------------------------------------------------

        metrics_required_columns = [
            "model",
            "train_start_year",
            "train_end_year",
            "test_year",
            "MAE_kg_ha",
            "RMSE_kg_ha",
            "R2",
            "MAPE_percent",
            "MAPE_derived_score",
        ]

        missing_metric_columns = [
            column
            for column in metrics_required_columns
            if column not in metrics_df.columns
        ]

        if missing_metric_columns:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": (
                        "2025 model comparison file "
                        "has missing columns."
                    ),
                    "missing_columns": missing_metric_columns,
                },
            )

        # -------------------------------------------------
        # Use only the verified RandomForest experiment
        # -------------------------------------------------

        rf_df = df[
            df["model"].astype(str).str.lower()
            == "randomforest"
        ].copy()

        if rf_df.empty:
            raise HTTPException(
                status_code=500,
                detail=(
                    "RandomForest results were not found "
                    "in the 2025 experimental district file."
                ),
            )

        rf_metrics = metrics_df[
            metrics_df["model"].astype(str).str.lower()
            == "randomforest"
        ].copy()

        if rf_metrics.empty:
            raise HTTPException(
                status_code=500,
                detail=(
                    "RandomForest metrics were not found "
                    "in the 2025 model comparison file."
                ),
            )

        # -------------------------------------------------
        # Find requested district
        # -------------------------------------------------

        district_rows = rf_df[
            rf_df["district"].astype(str).str.lower()
            == district.lower()
        ].copy()

        if district_rows.empty:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown district: {district}",
            )

        # -------------------------------------------------
        # Get district result
        # -------------------------------------------------

        row = district_rows.iloc[0]
        metrics = rf_metrics.iloc[0]

        actual = float(row["actual_2025_kg_ha"])
        predicted = float(row["predicted_2025_kg_ha"])
        error = float(row["error_kg_ha"])
        abs_error = float(row["abs_error_kg_ha"])
        pct_error = float(row["pct_error"])

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------

        return {
            "target_year": 2025,
            "district": str(row["district"]),

            "prediction_type": (
                "experimental_out_of_sample_hindcast"
            ),

            "actual_target_available": True,

            "model": {
                "name": "RandomForest",
                "training_period": "1997-2024",
                "test_year": 2025,
            },

            "prediction": {
                "predicted_yield_kg_ha": round(
                    predicted,
                    2,
                ),
            },

            "actual": {
                "yield_kg_ha": round(
                    actual,
                    2,
                ),
                "source": (
                    "2025-26 Third Advance Estimate"
                ),
            },

            "error": {
                "error_kg_ha": round(
                    error,
                    2,
                ),
                "abs_error_kg_ha": round(
                    abs_error,
                    2,
                ),
                "pct_error": round(
                    pct_error,
                    2,
                ),
            },

            "overall_metrics": {
                "MAE_kg_ha": round(
                    float(metrics["MAE_kg_ha"]),
                    2,
                ),
                "RMSE_kg_ha": round(
                    float(metrics["RMSE_kg_ha"]),
                    2,
                ),
                "R2": round(
                    float(metrics["R2"]),
                    4,
                ),
                "MAPE_percent": round(
                    float(metrics["MAPE_percent"]),
                    2,
                ),
                "MAPE_derived_score": round(
                    float(metrics["MAPE_derived_score"]),
                    2,
                ),
            },

            "source": (
                "backend/ml/evaluation/"
                "experimental_2025_train_to_2024/"
                "2025_out_of_sample_district_results.csv"
            ),

            "note": (
                "This is an experimental end-of-season "
                "hindcast using observed 2025 weather. "
                "It is not the production model output. "
                "The production GradientBoosting model "
                "remains unchanged."
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.error("2025 experimental forecast internal error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving 2025 forecast results.",
        )


# =========================================================
# 2026 EXPERIMENTAL SCENARIO-BASED FORECAST
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
        # Verified 2026 experimental prediction file
        # -------------------------------------------------

        prediction_path = PREDICTIONS_2026_PATH

        if not prediction_path.exists():
            raise HTTPException(
                status_code=404,
                detail="2026 experimental scenario predictions are not available.",
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
                    "message": (
                        "2026 prediction file has missing columns."
                    ),
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
        # Keep scenario order:
        # Dry -> Normal -> Wet
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
        # Build scenario response
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

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return {
            "target_year": 2026,
            "district": str(
                district_rows.iloc[0]["district"]
            ),
            "prediction_type": (
                "scenario_based_experimental_prediction"
            ),
            "actual_target_available": False,
            "data_provenance": {
                "origin_features": "Historical features up to 2024",
                "weather_assumption": "Pre-season IMD weather scenarios (Dry: 80% monsoon rain, Normal: 100%, Wet: 120%)",
                "satellite_status": "Unobserved for 2026; not used in 2026 scenario prediction",
                "actual_yield_status": "Pending 2026-27 Government of Maharashtra final advance estimates",
            },
            "source": (
                "data/"
                "cotton_2026_experimental_predictions.csv"
            ),
            "scenarios": scenarios,
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.error("2026 experimental forecast internal error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving 2026 scenario predictions.",
        )


# =========================================================
# EXISTING 2027-2031 DISTRICT FORECAST ROUTE
# =========================================================

@router.get("/{district}")
def future_forecast(district: str):
    """
    Return the existing 2027-2031 forecast
    for a single district.

    This uses the existing future forecasting system.
    """

    try:
        return forecast_district(district)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileNotFoundError as exc:
        logger.error("Future forecast artifact missing: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Future forecast model artifacts are not available.",
        )

    except Exception as exc:
        logger.error("Future forecast internal error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while generating the future forecast.",
        )