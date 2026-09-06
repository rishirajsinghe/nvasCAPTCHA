def get_decision(risk_score: float) -> tuple[str, str]:
    """
    Takes a risk score [0.0, 1.0] and returns an (action, reason) tuple based on
    configurable thresholds.
    """
    # Configurable thresholds
    ALLOW_THRESHOLD = 0.39
    CAPTCHA_THRESHOLD = 0.69
    
    if risk_score <= ALLOW_THRESHOLD:
        return "allow", "Behavioural interaction appears normal"
    elif risk_score <= CAPTCHA_THRESHOLD:
        return "captcha", "Suspicious interaction patterns detected"
    else:
        return "block", "Highly abnormal or impossible interaction timings"
