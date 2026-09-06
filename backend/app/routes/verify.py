from fastapi import APIRouter
from app.schemas.verify_schema import VerifyRequest, VerifyResponse
from app.services import verify_service

router = APIRouter()

@router.post("/verify", response_model=VerifyResponse)
def verify_behavior(payload: VerifyRequest):
    """
    Accepts behavioral and environmental feature data,
    evaluates it using the verification service, and returns a risk score.
    """
    result = verify_service.evaluate_features(payload)
    return result
