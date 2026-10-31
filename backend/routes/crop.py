import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from backend.schemas.request_schemas import CropRecommendRequest
from backend.ml.predictor import predictor_instance
from backend.database.db import save_prediction
from backend.ml.data_provenance_registry import (
    load_provenance_registry,
    get_datasets_by_classification
)

logger = logging.getLogger("agripredict.crop")

router = APIRouter()

AUTHENTIC_PANEL_PATH = Path("C:/Users/karta/.gemini/antigravity/scratch/AgriPredict-AI/data/authentic/processed/maharashtra_authentic_multi_crop_panel.csv")

@router.post("/api/crop/recommend")
def recommend_crop(req: CropRecommendRequest):
    try:
        inputs = req.model_dump()
        result = predictor_instance.predict_suitability(inputs)

        # Save query to history SQLite DB (isolated transaction)
        try:
            recs = result.get("recommendations", [])
            top_yield = recs[0]["predicted_yield_ha"] if recs else 0.0

            save_prediction(
                district=req.district,
                season=req.season,
                recommended_crop="Cotton",
                tomato_suitability=None,
                onion_suitability=None,
                sugarcane_suitability=None,
                predicted_yield=top_yield,
                inputs=inputs
            )
        except Exception as db_err:
            logger.warning("Could not persist crop recommendation to database: %s", db_err)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Crop suitability analysis error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred during crop suitability analysis.")

@router.get("/api/crop/authentic-overview")
def get_authentic_crops_overview():
    """Retrieve statistical overview of authentic historical observations for Tomato, Onion, and Sugarcane."""
    if not AUTHENTIC_PANEL_PATH.exists():
        raise HTTPException(status_code=404, detail="Authentic crop panel not found")
        
    df = pd.read_csv(AUTHENTIC_PANEL_PATH)
    crops_summary = {}
    for crop_name in ["Sugarcane", "Onion", "Tomato"]:
        c_df = df[df["crop"] == crop_name]
        crops_summary[crop_name] = {
            "total_records": len(c_df),
            "years": [int(c_df["year"].min()), int(c_df["year"].max())] if len(c_df) > 0 else [],
            "districts": sorted(c_df["district"].unique().tolist()),
            "mean_yield_t_ha": round(float(c_df["calculated_yield_t_ha"].mean()), 2) if len(c_df) > 0 else 0.0,
            "min_yield_t_ha": round(float(c_df["calculated_yield_t_ha"].min()), 2) if len(c_df) > 0 else 0.0,
            "max_yield_t_ha": round(float(c_df["calculated_yield_t_ha"].max()), 2) if len(c_df) > 0 else 0.0,
            "source_institutions": sorted(c_df["source_institution"].unique().tolist())
        }
        
    return {
        "status": "success",
        "data_provenance": "authentic_official_observation",
        "total_authentic_observations": len(df),
        "crops": crops_summary,
        "verification_summary": {
            "verified_matches": int((df["verification_status"] == "verified_match").sum()),
            "discrepancies_flagged": int((df["verification_status"] == "discrepancy_flagged").sum()),
            "calculation_formula": "Calculated_Yield = Production_Tonnes / Cultivated_Area_Ha"
        }
    }

@router.get("/api/crop/authentic-records")
def list_authentic_crop_records(
    crop: Optional[str] = Query(None, description="Filter by crop (Sugarcane, Onion, Tomato)"),
    district: Optional[str] = Query(None, description="Filter by Maharashtra district"),
    limit: int = Query(50, ge=1, le=200)
):
    """Query authentic historical agricultural records from official DES / NHB / Sugar Commissionerate sources."""
    if not AUTHENTIC_PANEL_PATH.exists():
        raise HTTPException(status_code=404, detail="Authentic crop panel not found")
        
    df = pd.read_csv(AUTHENTIC_PANEL_PATH)
    if crop:
        df = df[df["crop"].str.lower() == crop.strip().lower()]
    if district:
        df = df[df["district"].str.lower() == district.strip().lower()]
        
    records = df.head(limit).to_dict(orient="records")
    return {
        "status": "success",
        "count": len(records),
        "total_available": len(df),
        "data_provenance": "authentic_official_observation",
        "records": records
    }

@router.get("/api/crop/provenance-registry")
def get_provenance_registry():
    """Retrieve full permanent data provenance and authenticity registry."""
    try:
        return load_provenance_registry()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load provenance registry: {str(e)}")

