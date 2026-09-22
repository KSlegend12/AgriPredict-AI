from fastapi import APIRouter, HTTPException
from backend.schemas.request_schemas import YieldPredictRequest
from backend.ml.predictor import predictor_instance

router = APIRouter()

@router.post("/api/yield/predict")
def predict_yield(req: YieldPredictRequest):
    try:
        inputs = req.model_dump()
        result = predictor_instance.predict_yield_with_history(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yield prediction error: {str(e)}")
