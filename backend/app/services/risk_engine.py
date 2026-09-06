def calculate_baseline_risk(vector: dict) -> float:
    """
    Deterministic baseline scoring engine.
    Calculates a risk score between 0.0 (Human) and 1.0 (Bot) based on heuristics.
    This will be replaced by an ML model in the next phase.
    """
    risk_points = 0.0
    max_risk = 100.0
    
    # 1. Page Time Heuristics
    if vector["pageTime"] < 500:
        # Extremely fast interaction (< 500ms)
        risk_points += 40
    elif vector["pageTime"] > 300000 and vector["keyPressCount"] == 0 and vector["mouseDistance"] == 0:
        # Long time but absolutely zero interaction (suspicious headless ping)
        risk_points += 30
        
    # 2. Mouse Heuristics
    if not vector["hasTouch"]:
        if vector["mouseDistance"] == 0 and vector["clickCount"] > 0:
            # Clicking without moving mouse on a desktop
            risk_points += 50
        
        if vector["avgMouseSpeed"] > 20:
            # Impossibly fast average mouse speed (> 20px per millisecond)
            risk_points += 30
            
        if vector["mouseJitter"] > 20:
            # High jitter (lots of erratic >90deg snaps in <100ms)
            risk_points += 20
            
    # 3. Keyboard Heuristics
    if vector["keyPressCount"] > 0:
        if vector["avgKeyHoldDuration"] < 10:
            # Keys held for less than 10ms on average (superhuman speed)
            risk_points += 40
        if vector["avgKeyHoldDuration"] == 0:
            # Instantaneous keys (scripted)
            risk_points += 50
        if vector["repeatedKeyCount"] > vector["keyPressCount"] * 0.8:
            # If 80%+ of keystrokes are the exact same key repeatedly held/pressed
            risk_points += 30
            
    # 4. Interaction Heuristics
    if vector["clickCount"] > 50 and vector["pageTime"] < 5000:
        # > 10 clicks per second for 5 seconds
        risk_points += 60

    # Calculate final score [0.0, 1.0]
    final_score = min(risk_points / max_risk, 1.0)
    
    return final_score
