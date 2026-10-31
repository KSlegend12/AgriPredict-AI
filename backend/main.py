import os
import json
import logging

from fastapi import FastAPI, Response, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from backend.routes import (
    districts,
    weather,
    crop,
    yield_predict,
    history,
    field_validation
)

from backend.routes import cotton
from backend.routes.future_forecast import router as future_forecast_router

from backend.ml.predictor import predictor_instance
from backend.ml.cotton_predictor import cotton_predictor
from backend.security import RateLimitMiddleware, SecurityFilterMiddleware

logger = logging.getLogger("agripredict")
logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="AgriPredict AI — Vidarbha Cotton Decision Support",
    description=(
        "Post-Monsoon Pre-Harvest Cotton Yield Estimation and Decision Support System for Six Vidarbha Districts "
        "(Akola, Amravati, Buldhana, Nagpur, Wardha, Washim; validated model trained on 1997–2023 data, 2024 holdout)"
    ),
    version="2.2.0"
)


# =========================================================
# SECURITY & CORS MIDDLEWARE
# =========================================================
# Execution order: CORS -> SecurityFilter -> RateLimiter -> Router
_allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityFilterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# GLOBAL UNHANDLED EXCEPTION HANDLER
# =========================================================
# Prevents internal traceback leakage to HTTP clients

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "detail": "An internal error occurred while processing the request."
        }
    )



# =========================================================
# EXISTING ROUTES
# =========================================================

app.include_router(districts.router)
app.include_router(weather.router)
app.include_router(crop.router)
app.include_router(yield_predict.router)
app.include_router(history.router)


# =========================================================
# COTTON YIELD ROUTE
# =========================================================

app.include_router(cotton.router)
app.include_router(future_forecast_router)
app.include_router(field_validation.router)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
@app.get("/api/health")
def health_check():

    # -----------------------------------------------------
    # Existing crop model metrics
    # -----------------------------------------------------

    crop_metrics = getattr(
        predictor_instance,
        "metrics",
        {
            "classifier": {
                "accuracy": 0.9717
            },
            "regressor": {
                "r2_score": 0.9736,
                "mae": 1.61,
                "rmse": 3.56
            }
        }
    )


    # -----------------------------------------------------
    # Cotton model metadata
    # -----------------------------------------------------

    cotton_metadata = (
        cotton_predictor.metadata
        if cotton_predictor.is_loaded
        else {}
    )


    cotton_validation = (
        cotton_metadata.get(
            "validation_metrics_2011_2023",
            {}
        )
    )


    cotton_holdout = (
        cotton_metadata.get(
            "holdout_2024_metrics",
            {}
        )
    )


    # -----------------------------------------------------
    # Health response
    # -----------------------------------------------------

    return {

        "status":
            "online",

        "app_name":
            "AgriPredict AI",

        "version":
            "2.0.0",

        "geographic_scope":
            "Maharashtra, India",

        "crop":
            "Cotton",

        "supported_districts": [
            "Akola",
            "Amravati",
            "Buldhana",
            "Nagpur",
            "Wardha",
            "Washim"
        ],

        "modules": {

            # =============================================
            # Cotton suitability module (Cotton only)
            # =============================================

            "crop_suitability": {

                "crops": [
                    "Cotton"
                ],

                "is_loaded":
                    getattr(
                        predictor_instance,
                        "is_loaded",
                        False
                    ),

                "metrics":
                    crop_metrics
            },


            # =============================================
            # Cotton yield module
            # =============================================

            "cotton_yield_vidarbha": {

                "crop":
                    "Cotton",

                "districts": [
                    "Akola",
                    "Amravati",
                    "Buldhana",
                    "Nagpur",
                    "Wardha",
                    "Washim"
                ],


                # -----------------------------------------
                # Model
                # -----------------------------------------

                "model":
                    cotton_metadata.get(
                        "model_name",
                        "GradientBoosting"
                    ),

                "is_loaded":
                    cotton_predictor.is_loaded,


                # -----------------------------------------
                # Training
                # -----------------------------------------

                "training_years":
                    cotton_metadata.get(
                        "training_years",
                        "1997–2023"
                    ),

                "training_rows":
                    cotton_metadata.get(
                        "num_rows_train",
                        187
                    ),


                # -----------------------------------------
                # Validation
                # -----------------------------------------

                "validation_period":
                    "2011–2023",

                "temporal_folds":
                    "2011–2023 (13-fold expanding window)",

                "validation_mae_kg_ha":
                    cotton_validation.get(
                        "Mean_MAE"
                    ),

                "validation_rmse_kg_ha":
                    cotton_validation.get(
                        "Mean_RMSE"
                    ),

                "validation_r2":
                    cotton_validation.get(
                        "Mean_R2"
                    ),

                "validation_mape_percent":
                    cotton_validation.get(
                        "Mean_MAPE"
                    ),


                # -----------------------------------------
                # Final holdout
                # -----------------------------------------

                "holdout_year":
                    cotton_metadata.get(
                        "holdout_year",
                        2024
                    ),

                "holdout_mae_kg_ha":
                    cotton_holdout.get(
                        "MAE"
                    ),

                "holdout_rmse_kg_ha":
                    cotton_holdout.get(
                        "RMSE"
                    ),

                "holdout_r2":
                    cotton_holdout.get(
                        "R2"
                    ),

                "holdout_mape_percent":
                    cotton_holdout.get(
                        "MAPE"
                    ),


                # -----------------------------------------
                # Baselines
                # -----------------------------------------

                "baseline_2024": {

                    "previous_year_mae_kg_ha":
                        cotton_metadata
                        .get(
                            "baseline_2024",
                            {}
                        )
                        .get(
                            "PrevYear_MAE"
                        ),

                    "historical_mean_mae_kg_ha":
                        cotton_metadata
                        .get(
                            "baseline_2024",
                            {}
                        )
                        .get(
                            "HistMean_MAE"
                        )
                }
            }
        }
    }


# =========================================================
# READINESS CHECK
# =========================================================

@app.get("/api/ready")
def readiness_check(response: Response):
    """Readiness probe — reports whether all models are loaded.
    Returns 503 if any model is not loaded; 200 if all ready."""

    cotton_ready = cotton_predictor.is_loaded
    crop_ready = getattr(predictor_instance, "is_loaded", False)

    all_ready = cotton_ready and crop_ready

    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ready": all_ready,
        "models": {
            "cotton_yield": {
                "loaded": cotton_ready,
            },
            "crop_suitability": {
                "loaded": crop_ready,
            },
        },
    }


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )