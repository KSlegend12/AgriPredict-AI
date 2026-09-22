from fastapi import APIRouter
from backend.database.db import get_history

router = APIRouter()

@router.get("/api/history")
def read_history(limit: int = 50):
    records = get_history(limit=limit)
    return {
        "status": "success",
        "total": len(records),
        "history": records
    }
