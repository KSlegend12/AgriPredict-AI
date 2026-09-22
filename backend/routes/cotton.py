"""
Cotton yield prediction API routes for the 7 Vidarbha districts.
"""

from fastapi import APIRouter, HTTPException

from backend.schemas.request_schemas import CottonYieldPredictRequest
from backend.ml.cotton_predictor import cotton_predictor, VALID_DISTRICTS
from backend.services.cotton_input_builder import cotton_input_builder

router = APIRouter(prefix="/api/cotton", tags=["Cotton Yield"])


@router.post("/predict")
def predict_cotton_yield(req: CottonYieldPredictRequest):
    """Build the exact model feature row from verified historical data and predict."""
    try:
        built = cotton_input_builder.build(req.district, req.target_year)
        result = cotton_predictor.predict(built["features"])

        if result.get("status") == "error":
            raise HTTPException(status_code=422, detail=result.get("message"))

        result["prediction_input"] = {
            "district": req.district,
            "target_year": req.target_year,
            "data_source": built["source"],
            "missing_features": built["missing_features"]
        }
        result["prediction_status"] = (
            "historical_holdout_evaluation_year"
            if req.target_year == 2024
            else "historical_model_estimate"
        )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cotton yield prediction error: {str(e)}")


@router.get("/input/{district}/{year}")
def get_prediction_input(district: str, year: int):
    """Return the verified model inputs used for a district/year prediction."""
    try:
        return {"status": "success", **cotton_input_builder.build(district, year)}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/weather/{district}/{year}")
def get_cotton_weather(district: str, year: int):
    try:
        return {"status": "success", **cotton_input_builder.weather_summary(district, year)}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/history/{district}")
def get_cotton_history(district: str):
    try:
        return {"status": "success", **cotton_input_builder.history(district)}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/districts")
def list_districts():
    districts_info = []
    for dist in VALID_DISTRICTS:
        hist = cotton_predictor._get_district_history(dist)
        districts_info.append(hist if hist else {"district": dist, "note": "Historical data not loaded"})

    return {
        "status": "success",
        "geographic_scope": "Vidarbha Region, Maharashtra, India",
        "crop": "Cotton (Gossypium hirsutum)",
        "total_districts": len(VALID_DISTRICTS),
        "districts": districts_info,
        "supported_prediction_years": cotton_input_builder.available_years,
    }


@router.get("/model/info")
def model_info():
    if not cotton_predictor.is_loaded:
        raise HTTPException(status_code=503, detail="Cotton yield model not loaded.")

    meta = cotton_predictor.metadata
    return {
        "status": "success",
        "model_name": meta.get("model_name"),
        "crop": "Cotton (Gossypium hirsutum)",
        "geographic_scope": "7 Vidarbha districts, Maharashtra, India",
        "training_years": meta.get("training_years"),
        "num_training_rows": meta.get("num_rows_train", meta.get("num_rows")),
        "temporal_validation": {
            "strategy": "Expanding-window chronological (rolling-origin)",
            "test_folds": "2011–2023 (13 folds)",
            "holdout": "2024",
            "leakage_prevention": "2024 remains an untouched final holdout",
        },
        "validation_metrics": meta.get("validation_metrics_2011_2023"),
        "holdout_2024_metrics": meta.get("holdout_2024_metrics"),
        "total_features": len(meta.get("feature_cols", [])),
        "feature_cols": meta.get("feature_cols"),
        "top_10_features": cotton_predictor.feature_importance[:10],
        "all_models_comparison": meta.get("all_models_summary"),
        "is_model_loaded": cotton_predictor.is_loaded,
        "supported_prediction_years": cotton_input_builder.available_years,
    }
