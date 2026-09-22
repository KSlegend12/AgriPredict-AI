import os
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import (
    districts,
    weather,
    crop,
    yield_predict,
    history
)

from backend.routes import cotton
from backend.routes.future_forecast import router as future_forecast_router

from backend.ml.predictor import predictor_instance
from backend.ml.cotton_predictor import cotton_predictor


app = FastAPI(
    title="AgriPredict AI Backend",
    description=(
        "AIML Decision-Support System for Maharashtra Farmers — "
        "Crop suitability (Tomato, Onion, Sugarcane) + "
        "Cotton Yield Prediction for 7 Vidarbha districts "
        "(validated model trained on 1997–2023 data)"
    ),
    version="2.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


        "modules": {

            # =============================================
            # Existing crop suitability module
            # =============================================

            "crop_suitability": {

                "crops": [
                    "Tomato",
                    "Onion",
                    "Sugarcane"
                ],

                "is_loaded":
                    getattr(
                        predictor_instance,
                        "is_loaded",
                        True
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
                    "Washim",
                    "Yavatmal"
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