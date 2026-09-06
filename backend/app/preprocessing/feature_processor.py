from app.schemas.verify_schema import VerifyRequest

def preprocess_features(payload: VerifyRequest) -> dict:
    """
    Normalizes and cleans the raw request into a structured numerical vector.
    For this baseline phase, we just extract the relevant numerical values
    and handle any potential outliers or extreme edge cases safely.
    """
    
    b = payload.behavior
    e = payload.environment
    
    # Cap extreme values to prevent overflow in heuristic calculations
    page_time = min(b.pageTime, 3600000) # Max 1 hour
    
    # Simple dictionary representation of the feature vector
    vector = {
        # Mouse features
        "avgMouseSpeed": min(b.avgMouseSpeed, 100.0), # cap pixels/ms
        "clickCount": min(b.clickCount, 1000),
        "mouseDistance": min(b.mouseDistance, 100000.0),
        "mouseJitter": min(b.mouseJitter, 500),
        
        # Keyboard features
        "keyPressCount": min(b.keyPressCount, 5000),
        "avgKeyHoldDuration": min(b.avgKeyHoldDuration, 5000.0), # Cap at 5s hold
        "typingRate": min(b.typingRate, 1000.0),
        "backspaceCount": min(b.backspaceCount, 500),
        "repeatedKeyCount": min(b.repeatedKeyCount, 500),
        
        # Scroll features
        "scrollEventCount": min(b.scrollEventCount, 5000),
        "totalScrollDistance": min(b.totalScrollDistance, 500000.0),
        "scrollDirectionChanges": min(b.scrollDirectionChanges, 1000),
        
        # Interaction
        "pageTime": page_time,
        "fieldInteractionCount": min(b.fieldInteractionCount, 500),
        
        # Environment meta (can be used for heuristics)
        "hasTouch": e.touchSupport,
        "screenArea": e.screenResolution.width * e.screenResolution.height
    }
    
    return vector
