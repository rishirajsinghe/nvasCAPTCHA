import os
import random
import pandas as pd
import numpy as np

def clip(value, min_v, max_v):
    return max(min_v, min(value, max_v))

def get_screen_area():
    return random.choice([2073600, 1049088, 304500, 1440000])

def generate_profile(profile_name, label):
    # Base feature template
    f = {
        "avgMouseSpeed": 0.0, "clickCount": 0, "mouseDistance": 0.0, "mouseJitter": 0,
        "keyPressCount": 16, "avgKeyHoldDuration": 0.0, "typingRate": 0.0,
        "backspaceCount": 0, "repeatedKeyCount": 0, "scrollEventCount": 0,
        "totalScrollDistance": 0.0, "scrollDirectionChanges": 0, "pageTime": 0.0,
        "fieldInteractionCount": 2, "hasTouch": False, "screenArea": get_screen_area()
    }
    
    f["hasTouch"] = random.random() < 0.2
    
    if profile_name == "FAST_HUMAN":
        f["typingRate"] = clip(np.random.normal(500, 80), 300, 800)
        f["avgKeyHoldDuration"] = clip(np.random.normal(40, 10), 20, 80)
        f["pageTime"] = clip(np.random.normal(2000, 500), 1000, 4000)
        f["avgMouseSpeed"] = clip(np.random.normal(3.0, 1.0), 1.0, 8.0)
        f["mouseDistance"] = clip(np.random.normal(2500, 1000), 1000, 6000)
        f["mouseJitter"] = int(clip(np.random.normal(5, 2), 1, 15))
        f["clickCount"] = int(clip(np.random.normal(4, 1), 2, 8))
        f["scrollEventCount"] = int(clip(np.random.normal(2, 1), 0, 8))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(150, 50), 50, 300)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(0.5, 0.5), 0, 2))
        f["backspaceCount"] = int(clip(np.random.normal(1, 1), 0, 4))
        f["repeatedKeyCount"] = int(clip(np.random.normal(0, 1), 0, 2))

    elif profile_name == "SLOW_HUMAN":
        f["typingRate"] = clip(np.random.normal(150, 40), 50, 300)
        f["avgKeyHoldDuration"] = clip(np.random.normal(120, 30), 60, 250)
        f["pageTime"] = clip(np.random.normal(15000, 5000), 5000, 40000)
        f["avgMouseSpeed"] = clip(np.random.normal(0.8, 0.3), 0.1, 2.0)
        f["mouseDistance"] = clip(np.random.normal(1000, 500), 200, 3000)
        f["mouseJitter"] = int(clip(np.random.normal(2, 1), 0, 8))
        f["clickCount"] = int(clip(np.random.normal(3, 1), 1, 6))
        f["scrollEventCount"] = int(clip(np.random.normal(1, 1), 0, 5))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(100, 50), 20, 200)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(1, 1), 0, 3))
        f["backspaceCount"] = int(clip(np.random.normal(2, 2), 0, 8))
        f["fieldInteractionCount"] = int(clip(np.random.normal(4, 2), 2, 10))

    elif profile_name == "LOW_ACTIVITY_HUMAN":
        f["typingRate"] = clip(np.random.normal(250, 60), 100, 450)
        f["avgKeyHoldDuration"] = clip(np.random.normal(80, 20), 40, 150)
        f["pageTime"] = clip(np.random.normal(3000, 1000), 1500, 10000)
        f["avgMouseSpeed"] = clip(np.random.normal(0.5, 0.5), 0.0, 2.0)
        f["mouseDistance"] = clip(np.random.normal(300, 200), 0, 1000)
        f["mouseJitter"] = int(clip(np.random.normal(0.5, 0.5), 0, 2))
        f["clickCount"] = int(clip(np.random.normal(1.5, 0.5), 1, 3))
        f["scrollEventCount"] = int(clip(np.random.normal(0.1, 0.3), 0, 2))
        f["totalScrollDistance"] = f["scrollEventCount"] * 50
        f["scrollDirectionChanges"] = 0
        f["backspaceCount"] = 0
        f["fieldInteractionCount"] = 2

    elif profile_name == "ERRATIC_HUMAN":
        f["typingRate"] = clip(np.random.normal(300, 150), 50, 800)
        f["avgKeyHoldDuration"] = clip(np.random.normal(90, 50), 20, 300)
        f["pageTime"] = clip(np.random.normal(8000, 6000), 2000, 30000)
        f["avgMouseSpeed"] = clip(np.random.normal(2.5, 2.0), 0.1, 10.0)
        f["mouseDistance"] = clip(np.random.normal(3000, 2500), 500, 15000)
        f["mouseJitter"] = int(clip(np.random.normal(8, 5), 0, 25))
        f["clickCount"] = int(clip(np.random.normal(6, 4), 2, 20))
        f["scrollEventCount"] = int(clip(np.random.normal(5, 4), 0, 20))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(200, 150), 50, 1000)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(3, 2), 0, 10))
        f["backspaceCount"] = int(clip(np.random.normal(3, 3), 0, 15))
        f["repeatedKeyCount"] = int(clip(np.random.normal(1.5, 1.5), 0, 6))
        f["fieldInteractionCount"] = int(clip(np.random.normal(5, 3), 2, 15))

    elif profile_name == "POWER_USER_HUMAN":
        f["typingRate"] = clip(np.random.normal(600, 100), 400, 1000)
        f["avgKeyHoldDuration"] = clip(np.random.normal(35, 8), 15, 60)
        f["pageTime"] = clip(np.random.normal(1500, 400), 800, 3000)
        f["avgMouseSpeed"] = clip(np.random.normal(5.0, 1.5), 2.0, 12.0)
        f["mouseDistance"] = clip(np.random.normal(4000, 1500), 1500, 10000)
        f["mouseJitter"] = int(clip(np.random.normal(3, 1), 0, 8))
        f["clickCount"] = int(clip(np.random.normal(2, 0.5), 1, 4))
        f["scrollEventCount"] = int(clip(np.random.normal(1, 0.5), 0, 3))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(300, 100), 100, 800)
        f["scrollDirectionChanges"] = 0
        f["backspaceCount"] = int(clip(np.random.normal(0.5, 0.8), 0, 3))
        f["fieldInteractionCount"] = 2

    # BOTS
    elif profile_name == "HUMAN_MIMIC_BOT":
        # Mimics typical human values but might have tight variances
        f["typingRate"] = clip(np.random.normal(280, 20), 100, 500)
        f["avgKeyHoldDuration"] = clip(np.random.normal(85, 5), 40, 150)
        f["pageTime"] = clip(np.random.normal(4500, 200), 2000, 10000)
        f["avgMouseSpeed"] = clip(np.random.normal(1.3, 0.2), 0.5, 3.0)
        f["mouseDistance"] = clip(np.random.normal(1600, 100), 500, 4000)
        f["mouseJitter"] = int(clip(np.random.normal(2.5, 0.5), 0, 10))
        f["clickCount"] = int(clip(np.random.normal(3, 0.5), 2, 5))
        f["scrollEventCount"] = int(clip(np.random.normal(1.5, 0.5), 0, 5))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(180, 20), 50, 400)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(0.5, 0.5), 0, 2))
        f["backspaceCount"] = int(clip(np.random.normal(0.8, 0.2), 0, 5))
        f["fieldInteractionCount"] = int(clip(np.random.normal(3, 0.5), 2, 6))

    elif profile_name == "SLOW_BOT":
        f["typingRate"] = clip(np.random.normal(120, 10), 50, 200)
        f["avgKeyHoldDuration"] = clip(np.random.normal(150, 10), 80, 250)
        f["pageTime"] = clip(np.random.normal(20000, 500), 10000, 40000)
        f["avgMouseSpeed"] = clip(np.random.normal(0.5, 0.1), 0.1, 1.5)
        f["mouseDistance"] = clip(np.random.normal(800, 100), 200, 2000)
        f["mouseJitter"] = int(clip(np.random.normal(1, 0.5), 0, 5))
        f["clickCount"] = 2
        f["scrollEventCount"] = int(clip(np.random.normal(2, 0.5), 0, 5))
        f["totalScrollDistance"] = f["scrollEventCount"] * 100
        f["scrollDirectionChanges"] = 0

    elif profile_name == "ACTIVE_BOT":
        f["typingRate"] = clip(np.random.normal(350, 30), 200, 600)
        f["avgKeyHoldDuration"] = clip(np.random.normal(70, 10), 30, 120)
        f["pageTime"] = clip(np.random.normal(6000, 300), 3000, 15000)
        f["avgMouseSpeed"] = clip(np.random.normal(2.0, 0.2), 0.5, 5.0)
        f["mouseDistance"] = clip(np.random.normal(3500, 200), 1000, 8000)
        f["mouseJitter"] = int(clip(np.random.normal(4, 1), 0, 15))
        f["clickCount"] = int(clip(np.random.normal(8, 1), 4, 15))
        f["scrollEventCount"] = int(clip(np.random.normal(6, 1), 2, 12))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(250, 50), 100, 600)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(2, 0.5), 0, 5))
        f["fieldInteractionCount"] = int(clip(np.random.normal(6, 1), 4, 12))

    elif profile_name == "ERRATIC_BOT":
        # Adversarial randoms
        f["typingRate"] = np.random.uniform(50, 1000)
        f["avgKeyHoldDuration"] = np.random.uniform(10, 400)
        f["pageTime"] = np.random.uniform(1000, 50000)
        f["avgMouseSpeed"] = np.random.uniform(0.1, 15.0)
        f["mouseDistance"] = np.random.uniform(100, 20000)
        f["mouseJitter"] = int(np.random.uniform(0, 30))
        f["clickCount"] = int(np.random.uniform(1, 30))
        f["scrollEventCount"] = int(np.random.uniform(0, 30))
        f["totalScrollDistance"] = np.random.uniform(0, 5000)
        f["scrollDirectionChanges"] = int(np.random.uniform(0, 15))
        f["backspaceCount"] = int(np.random.uniform(0, 20))
        f["repeatedKeyCount"] = int(np.random.uniform(0, 15))
        f["fieldInteractionCount"] = int(np.random.uniform(2, 20))

    elif profile_name == "ADVERSARIAL_MIXED_BOT":
        # Draw from different realistic distributions independently
        f["typingRate"] = clip(np.random.normal(np.random.choice([200, 400, 600]), 50), 50, 1000)
        f["avgKeyHoldDuration"] = clip(np.random.normal(np.random.choice([40, 80, 120]), 15), 10, 300)
        f["pageTime"] = clip(np.random.normal(np.random.choice([2000, 5000, 10000]), 1000), 1000, 30000)
        f["avgMouseSpeed"] = clip(np.random.normal(np.random.choice([1.0, 3.0, 6.0]), 1.0), 0.1, 15.0)
        f["mouseDistance"] = clip(np.random.normal(np.random.choice([500, 2000, 5000]), 500), 0, 15000)
        f["mouseJitter"] = int(clip(np.random.normal(np.random.choice([1, 5, 10]), 2), 0, 25))
        f["clickCount"] = int(clip(np.random.normal(np.random.choice([2, 5, 10]), 2), 1, 20))
        f["scrollEventCount"] = int(clip(np.random.normal(np.random.choice([0, 3, 8]), 2), 0, 20))
        f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(150, 50), 0, 1000)
        f["scrollDirectionChanges"] = int(clip(np.random.normal(np.random.choice([0, 1, 3]), 1), 0, 10))
        f["backspaceCount"] = int(clip(np.random.normal(np.random.choice([0, 2, 5]), 2), 0, 15))
        f["repeatedKeyCount"] = int(clip(np.random.normal(np.random.choice([0, 1, 3]), 1), 0, 10))
        f["fieldInteractionCount"] = int(clip(np.random.normal(np.random.choice([2, 4, 8]), 2), 2, 20))

    # General realistic constraint
    f["keyPressCount"] = 12 + f["backspaceCount"] + f["repeatedKeyCount"]
    if f["keyPressCount"] < 12: f["keyPressCount"] = 12
    if f["keyPressCount"] > 100: f["keyPressCount"] = 100

    row = {"true_label": label, "profile": profile_name}
    feature_names = [
        "avgMouseSpeed", "clickCount", "mouseDistance", "mouseJitter",
        "keyPressCount", "avgKeyHoldDuration", "typingRate", "backspaceCount",
        "repeatedKeyCount", "scrollEventCount", "totalScrollDistance",
        "scrollDirectionChanges", "pageTime", "fieldInteractionCount",
        "hasTouch", "screenArea"
    ]
    for n in feature_names:
        row[n] = float(f[n]) if isinstance(f[n], bool) else f[n]
    
    return row

def generate_adversarial_dataset():
    # Fix seed for reproducibility
    np.random.seed(424242)
    random.seed(424242)
    
    human_profiles = ["FAST_HUMAN", "SLOW_HUMAN", "LOW_ACTIVITY_HUMAN", "ERRATIC_HUMAN", "POWER_USER_HUMAN"]
    bot_profiles = ["HUMAN_MIMIC_BOT", "SLOW_BOT", "ACTIVE_BOT", "ERRATIC_BOT", "ADVERSARIAL_MIXED_BOT"]
    
    data = []
    
    for hp in human_profiles:
        for _ in range(100):
            data.append(generate_profile(hp, "human"))
            
    for bp in bot_profiles:
        for _ in range(100):
            data.append(generate_profile(bp, "bot"))
            
    df = pd.DataFrame(data)
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'adversarial_blind_test'))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "adversarial_blind_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} samples and saved to {out_path}")

if __name__ == "__main__":
    generate_adversarial_dataset()
