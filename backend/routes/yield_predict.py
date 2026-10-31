import logging
from fastapi import APIRouter, HTTPException
from backend.schemas.request_schemas import YieldPredictRequest
from backend.ml.predictor import predictor_instance
from backend.config import ALLOWED_CROPS

logger = logging.getLogger("agripredict.yield")

router = APIRouter()

@router.post("/api/yield/predict")
def predict_yield(req: YieldPredictRequest):
    if req.crop not in ALLOWED_CROPS:
        raise HTTPException(
            status_code=422,
            detail=f"Crop '{req.crop}' is not supported. AgriPredict-AI is strictly dedicated to Vidarbha Cotton Yield Prediction."
        )
    try:
        inputs = req.model_dump()
        result = predictor_instance.predict_yield_with_history(inputs)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Yield prediction error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during crop yield prediction.")
