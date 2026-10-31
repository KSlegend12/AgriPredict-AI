"""
Cotton yield prediction API routes for the 7 Vidarbha districts.
"""

from fastapi import APIRouter, HTTPException

from backend.schemas.request_schemas import CottonYieldPredictRequest
from backend.ml.cotton_predictor import cotton_predictor, VALID_DISTRICTS
from backend.services.cotton_input_builder import cotton_input_builder
from backend.ml.xai_engine import xai_engine
from backend.database.db import save_cotton_prediction

from typing import Optional
import logging

logger = logging.getLogger("agripredict.cotton")

router = APIRouter(prefix="/api/cotton", tags=["Cotton Yield"])


@router.post("/predict")
def predict_cotton_yield(req: CottonYieldPredictRequest):
    """Build the exact model feature row from verified historical data and predict."""
    if not cotton_predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Cotton yield prediction model is not currently available."
        )

    try:
        built = cotton_input_builder.build(req.district, req.target_year, model_version=req.model_version)
        result = cotton_predictor.predict(built["features"], model_version=req.model_version)

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

        try:
            interval = result.get("prediction_interval", {})
            pred_val = float(result.get("predicted_yield_kg_ha") or result.get("predicted_yield_kg_per_ha") or 0.0)
            save_cotton_prediction(
                district=req.district,
                year=req.target_year,
                predicted_yield=pred_val,
                lower_bound=float(interval.get("lower_bound_kg_per_ha", 0.0)) if interval else None,
                upper_bound=float(interval.get("upper_bound_kg_per_ha", 0.0)) if interval else None,
                model_type=req.model_version or "production",
                inputs=built.get("features", {})
            )
        except Exception as db_err:
            logger.warning("Could not persist cotton prediction to database: %s", db_err)

        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Cotton yield prediction internal error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the cotton yield prediction."
        )


@router.get("/input/{district}/{year}")
def get_prediction_input(district: str, year: int, model_version: Optional[str] = None):
    """Return the verified model inputs used for a district/year prediction."""
    try:
        return {"status": "success", **cotton_input_builder.build(district, year, model_version=model_version or "candidate_six_district_thermal")}
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
        "global_shap_importance": xai_engine.get_global_importance(),
        "all_models_comparison": meta.get("all_models_summary"),
        "candidate_model": {
            "available": cotton_predictor.candidate_is_loaded,
            "metadata": cotton_predictor.candidate_metadata if cotton_predictor.candidate_is_loaded else None
        },
        "candidate_delta_rolling": {
            "available": cotton_predictor.delta_is_loaded,
            "metadata": cotton_predictor.delta_metadata if cotton_predictor.delta_is_loaded else None
        },
        "candidate_regularized_ensemble": {
            "available": cotton_predictor.reg_ensemble_is_loaded,
            "metadata": cotton_predictor.reg_ensemble_metadata if cotton_predictor.reg_ensemble_is_loaded else None
        },
        "candidate_repaired_synth": {
            "available": getattr(cotton_predictor, "repaired_synth_is_loaded", False),
            "metadata": getattr(cotton_predictor, "repaired_synth_metadata", None) if getattr(cotton_predictor, "repaired_synth_is_loaded", False) else None
        },
        "candidate_physiological_ridge_a100": {
            "available": getattr(cotton_predictor, "phys_ridge_is_loaded", False),
            "metadata": getattr(cotton_predictor, "phys_ridge_metadata", None) if getattr(cotton_predictor, "phys_ridge_is_loaded", False) else None
        },
        "candidate_six_district_physiological": {
            "available": getattr(cotton_predictor, "six_dist_is_loaded", False),
            "metadata": getattr(cotton_predictor, "six_dist_metadata", None) if getattr(cotton_predictor, "six_dist_is_loaded", False) else None
        },
        "candidate_six_district_thermal": {
            "available": getattr(cotton_predictor, "six_dist_thermal_is_loaded", False),
            "metadata": getattr(cotton_predictor, "six_dist_thermal_metadata", None) if getattr(cotton_predictor, "six_dist_thermal_is_loaded", False) else None
        },
        "candidate_six_district_decoupled_agronomic": {
            "available": getattr(cotton_predictor, "decoupled_agronomic_is_loaded", False),
            "metadata": getattr(cotton_predictor, "decoupled_agronomic_metadata", None) if getattr(cotton_predictor, "decoupled_agronomic_is_loaded", False) else None
        },
        "candidate_six_district_dar_deficit_heat_thresh": {
            "available": getattr(cotton_predictor, "decoupled_deficit_heat_is_loaded", False),
            "metadata": getattr(cotton_predictor, "decoupled_deficit_heat_metadata", None) if getattr(cotton_predictor, "decoupled_deficit_heat_is_loaded", False) else None
        },
        "is_model_loaded": cotton_predictor.is_loaded,
        "supported_prediction_years": cotton_input_builder.available_years,
    }


@router.get("/xai/global")
def get_global_xai():
    """Return the global SHAP feature importance and explanation metadata."""
    return {"status": "success", **xai_engine.get_global_importance()}
