import os
import joblib
import logging
from app.ml.feature_schema import extract_feature_list

logger = logging.getLogger(__name__)

class MLPredictor:
    def __init__(self):
        self.model = None
        self.model_version = "baseline-v1"
        self._load_model()

    def _load_model(self):
        # The model path is relative to the backend root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        model_path = os.path.join(base_dir, "models", "nvas_captcha_model_v3.joblib")
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.model_version = "ml-v3"
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
        
        # Convert dict to ordered list for sklearn
        feature_list = extract_feature_list(vector)
        
        # scikit-learn expects 2D array: [samples, features]
        # predict_proba returns [[prob_class_0, prob_class_1]]
        # We assume class 1 is "bot".
        probabilities = self.model.predict_proba([feature_list])[0]
        
        # Depending on how classes were ordered during training...
        # Usually model.classes_ reveals this. Let's assume index 1 is "bot" (1.0).
        if hasattr(self.model, "classes_"):
            # If classes are [0, 1] or ['human', 'bot']
            # We will use 'human' and 'bot' as string labels.
            classes = list(self.model.classes_)
            if 'bot' in classes:
                bot_idx = classes.index('bot')
                return float(probabilities[bot_idx])
            elif 1 in classes:
                bot_idx = classes.index(1)
                return float(probabilities[bot_idx])
            
        # Fallback if classes_ isn't directly matching expected
        return float(probabilities[1])

predictor = MLPredictor()
