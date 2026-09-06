# This file defines the exact ordering and names of features for ML training and inference.
# Any changes here MUST be accompanied by retraining the model.

FEATURE_NAMES = [
    "avgMouseSpeed",
    "clickCount",
    "mouseDistance",
    "mouseJitter",
    "keyPressCount",
    "avgKeyHoldDuration",
    "typingRate",
    "backspaceCount",
    "repeatedKeyCount",
    "scrollEventCount",
    "totalScrollDistance",
    "scrollDirectionChanges",
    "pageTime",
    "fieldInteractionCount",
    "hasTouch",
    "screenArea"
]

def extract_feature_list(vector: dict) -> list:
    """
    Extracts numerical features from the vector dict in the exact order specified by FEATURE_NAMES.
    Returns a flat list of floats.
    """
    return [float(vector.get(feature, 0.0)) for feature in FEATURE_NAMES]
