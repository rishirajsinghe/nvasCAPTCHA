import sys

# Maintain EXACT V3 order first, then append V4 features
V4_FEATURE_NAMES = [
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
    "screenArea",
    
    # --- V4 Derived Features ---
    # SKIPPED: mouseSpeedStd, keyIntervalStd, mousePauseCount, etc. 
    # Reason: Not supported by existing aggregate SDK telemetry. Raw events are not currently captured.
    
    "interactionRate",         # fieldInteractionCount / pageTime(s)
    "keyboardActivityRate",    # keyPressCount / pageTime(s)
    "mouseActivityRate",       # mouseDistance / pageTime(s)
    "scrollRate",              # totalScrollDistance / pageTime(s)
    "clickRate",               # clickCount / pageTime(s)
    "mouseToKeyboardRatio"     # mouseDistance / keyPressCount
]

def derive_v4_features(f):
    page_time_s = max(f.get("pageTime", 1000) / 1000.0, 0.1)
    kb_count = max(f.get("keyPressCount", 0), 1)
    
    f["interactionRate"] = f.get("fieldInteractionCount", 0) / page_time_s
    f["keyboardActivityRate"] = f.get("keyPressCount", 0) / page_time_s
    f["mouseActivityRate"] = f.get("mouseDistance", 0.0) / page_time_s
    f["scrollRate"] = f.get("totalScrollDistance", 0.0) / page_time_s
    f["clickRate"] = f.get("clickCount", 0) / page_time_s
    f["mouseToKeyboardRatio"] = f.get("mouseDistance", 0.0) / kb_count
    
    return f

def extract_feature_list_v4(features_dict):
    f = dict(features_dict) # copy
    f = derive_v4_features(f)
    
    return [
        float(f.get("avgMouseSpeed", 0.0)),
        int(f.get("clickCount", 0)),
        float(f.get("mouseDistance", 0.0)),
        int(f.get("mouseJitter", 0)),
        int(f.get("keyPressCount", 0)),
        float(f.get("avgKeyHoldDuration", 0.0)),
        float(f.get("typingRate", 0.0)),
        int(f.get("backspaceCount", 0)),
        int(f.get("repeatedKeyCount", 0)),
        int(f.get("scrollEventCount", 0)),
        float(f.get("totalScrollDistance", 0.0)),
        int(f.get("scrollDirectionChanges", 0)),
        float(f.get("pageTime", 0.0)),
        int(f.get("fieldInteractionCount", 0)),
        int(bool(f.get("hasTouch", False))),
        int(f.get("screenArea", 2073600)),
        
        float(f.get("interactionRate", 0.0)),
        float(f.get("keyboardActivityRate", 0.0)),
        float(f.get("mouseActivityRate", 0.0)),
        float(f.get("scrollRate", 0.0)),
        float(f.get("clickRate", 0.0)),
        float(f.get("mouseToKeyboardRatio", 0.0))
    ]
