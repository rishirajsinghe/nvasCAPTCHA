from fastapi import APIRouter
from app.database.mongodb import db

router = APIRouter()

@router.get("/health")
def health_check():
    db_status = "connected" if db.is_connected() else "disconnected"
    return {
        "status": "ok",
        "service": "nvasCAPTCHA",
        "database": db_status
    }
