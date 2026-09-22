from fastapi import APIRouter
from backend.config import MAHARASHTRA_DISTRICTS, ALLOWED_CROPS

router = APIRouter()

@router.get("/api/districts")
def get_districts():
    district_list = []
    for d_name, d_data in MAHARASHTRA_DISTRICTS.items():
        district_list.append({
            "name": d_name,
            "region": d_data["region"],
            "lat": d_data["lat"],
            "lon": d_data["lon"],
            "avg_rainfall": d_data["avg_rainfall"]
        })
    return {
        "status": "success",
        "state": "Maharashtra",
        "total_districts": len(district_list),
        "allowed_crops": ALLOWED_CROPS,
        "districts": district_list
    }
