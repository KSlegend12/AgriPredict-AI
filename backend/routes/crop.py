from fastapi import APIRouter, HTTPException
from backend.schemas.request_schemas import CropRecommendRequest
from backend.ml.predictor import predictor_instance
from backend.database.db import save_prediction

router = APIRouter()

@router.post("/api/crop/recommend")
def recommend_crop(req: CropRecommendRequest):
    try:
        inputs = req.model_dump()
        result = predictor_instance.predict_suitability(inputs)

        # Save query to history SQLite DB
        recs = result["recommendations"]
        tomato_suit = next((r["suitability_percentage"] for r in recs if r["crop"] == "Tomato"), 0.0)
        onion_suit = next((r["suitability_percentage"] for r in recs if r["crop"] == "Onion"), 0.0)
        sugarcane_suit = next((r["suitability_percentage"] for r in recs if r["crop"] == "Sugarcane"), 0.0)
        top_yield = recs[0]["predicted_yield_ha"] if recs else 0.0

        save_prediction(
            district=req.district,
            season=req.season,
            recommended_crop=result["recommended_crop"],
            tomato_suitability=tomato_suit,
            onion_suitability=onion_suit,
            sugarcane_suitability=sugarcane_suit,
            predicted_yield=top_yield,
            inputs=inputs
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop suitability analysis error: {str(e)}")
