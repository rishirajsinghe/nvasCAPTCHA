import os
import uuid
import logging
from datetime import datetime, timezone
from app.schemas.verify_schema import VerifyRequest, VerifyResponse
from app.preprocessing import feature_processor
from app.services import risk_engine
from app.services import decision_engine
from app.database.mongodb import db
from app.ml.predictor_v4 import predictor_v4 as predictor

logger = logging.getLogger(__name__)

def evaluate_features(payload: VerifyRequest) -> dict:
    session_id = str(uuid.uuid4())
    vector = feature_processor.preprocess_features(payload)
    
    # ML Pipeline / Fallback
    if predictor.is_available():
        try:
            risk_score = predictor.predict_risk(vector)
            model_version = predictor.model_version
        except Exception as e:
            logger.error(f"ML Prediction failed: {e}. Falling back to baseline.")
            risk_score = risk_engine.calculate_baseline_risk(vector)
            model_version = "baseline-v1"
    else:
        risk_score = risk_engine.calculate_baseline_risk(vector)
        model_version = "baseline-v1"
    
    # Decision
    action, reason = decision_engine.get_decision(risk_score)
    
    # Database Logging
    record = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "features": vector,
        "risk_score": round(risk_score, 4),
        "action": action,
        "reason": reason,
        "model_version": model_version
    }
    
    # Optional Data Collection Mode
    data_collection_mode = os.getenv("DATA_COLLECTION_MODE", "false").lower() == "true"
    if data_collection_mode:
        if payload.label is not None:
            record["label"] = payload.label
        if payload.source is not None:
            record["source"] = payload.source

    db.save_verification(record)
    
    return {
        "success": True,
        "riskScore": round(risk_score, 4),
        "action": action,
        "reason": reason,
        "session_id": session_id,
        "modelVersion": model_version
    }
