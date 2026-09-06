import os
import joblib
import logging
from app.ml.feature_schema_v4 import extract_feature_list_v4

logger = logging.getLogger(__name__)

class MLPredictorV4:
    def __init__(self):
        self.model = None
        self.model_version = "baseline-v1"
        self._load_model()

    def _load_model(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        model_path = os.path.join(base_dir, "models", "nvas_captcha_model_v4.joblib")
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.model_version = "ml-v4"
                logger.info(f"Successfully loaded ML model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}. Falling back to baseline.")
                self.model = None
        else:
            logger.warning(f"ML model not found at {model_path}. Falling back to baseline.")

    def is_available(self) -> bool:
        return self.model is not None

    def predict_risk(self, vector: dict) -> float:
        """
        Takes the flat dictionary vector, converts to ordered list, predicts bot probability.
        """
        if not self.is_available():
            raise RuntimeError("ML model is not loaded.")
        
        feature_list = extract_feature_list_v4(vector)
        
        probabilities = self.model.predict_proba([feature_list])[0]
        
        if hasattr(self.model, "classes_"):
            classes = list(self.model.classes_)
            if 'bot' in classes:
                bot_idx = classes.index('bot')
                return float(probabilities[bot_idx])
            elif 1 in classes:
                bot_idx = classes.index(1)
                return float(probabilities[bot_idx])
            
        return float(probabilities[1])

predictor_v4 = MLPredictorV4()
