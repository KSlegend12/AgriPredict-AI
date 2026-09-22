from fastapi import APIRouter, HTTPException
from backend.services.weather_service import fetch_district_weather

router = APIRouter()

@router.get("/api/weather/{district}")
async def get_district_weather(district: str):
    try:
        data = await fetch_district_weather(district)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve weather data for {district}.")
