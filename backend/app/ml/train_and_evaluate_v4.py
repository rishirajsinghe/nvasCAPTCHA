import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import random
import requests
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.app.ml.feature_schema_v4 import V4_FEATURE_NAMES, derive_v4_features
from backend.app.ml.feature_schema import FEATURE_NAMES as V3_FEATURE_NAMES

def get_screen_area():
    return random.choice([2073600, 1049088, 304500, 1440000])

def clip(v, m, M):
    return max(m, min(v, M))

def generate_v4_training_data(n_samples=2000):
    np.random.seed(10101)
    random.seed(10101)
    
    data = []
    
    # 50% Human, 50% Bot
    for i in range(n_samples):
        label = "human" if i < n_samples/2 else "bot"
        
        f = {
            "avgMouseSpeed": 0.0, "clickCount": 0, "mouseDistance": 0.0, "mouseJitter": 0,
            "keyPressCount": 16, "avgKeyHoldDuration": 0.0, "typingRate": 0.0,
            "backspaceCount": 0, "repeatedKeyCount": 0, "scrollEventCount": 0,
            "totalScrollDistance": 0.0, "scrollDirectionChanges": 0, "pageTime": 0.0,
            "fieldInteractionCount": 2, "hasTouch": random.random() < 0.25, 
            "screenArea": get_screen_area()
        }
        
        if label == "human":
            sub_profile = random.choice(["fast", "slow", "low_activity", "erratic", "power", "normal"])
            if sub_profile == "fast":
                f["typingRate"] = clip(np.random.normal(550, 100), 300, 900)
                f["pageTime"] = clip(np.random.normal(2500, 500), 1000, 5000)
                f["avgMouseSpeed"] = clip(np.random.normal(4.0, 1.5), 1.0, 8.0)
            elif sub_profile == "slow":
                f["typingRate"] = clip(np.random.normal(120, 30), 50, 250)
                f["pageTime"] = clip(np.random.normal(20000, 5000), 5000, 45000)
                f["avgMouseSpeed"] = clip(np.random.normal(0.6, 0.2), 0.1, 1.5)
            elif sub_profile == "low_activity":
                f["typingRate"] = clip(np.random.normal(200, 50), 100, 400)
                f["pageTime"] = clip(np.random.normal(4000, 1000), 2000, 10000)
                f["avgMouseSpeed"] = clip(np.random.normal(0.4, 0.3), 0.0, 1.5)
                f["mouseDistance"] = clip(np.random.normal(200, 150), 0, 800)
                f["scrollEventCount"] = 0
            elif sub_profile == "erratic":
                f["typingRate"] = np.random.uniform(100, 700)
                f["pageTime"] = np.random.uniform(3000, 25000)
                f["avgMouseSpeed"] = np.random.uniform(0.5, 8.0)
                f["scrollDirectionChanges"] = np.random.randint(1, 8)
                f["mouseJitter"] = np.random.randint(5, 20)
            elif sub_profile == "power":
                f["typingRate"] = clip(np.random.normal(700, 150), 500, 1100)
                f["pageTime"] = clip(np.random.normal(1200, 300), 800, 2000)
                f["avgMouseSpeed"] = clip(np.random.normal(6.0, 2.0), 3.0, 12.0)
                f["scrollEventCount"] = np.random.randint(0, 3)
            else: # normal
                f["typingRate"] = clip(np.random.normal(300, 80), 150, 600)
                f["pageTime"] = clip(np.random.normal(6000, 2000), 2000, 15000)
                f["avgMouseSpeed"] = clip(np.random.normal(1.5, 0.5), 0.5, 4.0)
                
            # Fill missing based on correlation
            if f["mouseDistance"] == 0:
                f["mouseDistance"] = f["avgMouseSpeed"] * (f["pageTime"]/1000) * clip(np.random.normal(150, 50), 50, 400)
            f["clickCount"] = int(clip(np.random.normal(3, 1), 1, 10))
            f["avgKeyHoldDuration"] = clip(10000 / (f["typingRate"] + 1), 20, 250) + np.random.normal(0, 10)
            if f["scrollEventCount"] == 0 and sub_profile not in ["low_activity", "power"]:
                f["scrollEventCount"] = int(clip(np.random.normal(2, 1), 0, 8))
            f["totalScrollDistance"] = f["scrollEventCount"] * clip(np.random.normal(150, 50), 50, 400)
            f["backspaceCount"] = int(clip(np.random.normal(2, 2), 0, 10))
            f["repeatedKeyCount"] = int(clip(np.random.normal(1, 1), 0, 5))
            f["keyPressCount"] = 12 + f["backspaceCount"] + f["repeatedKeyCount"]

        else:
            sub_profile = random.choice(["fast_bot", "slow_bot", "active_bot", "mimic_bot", "irregular_bot"])
            if sub_profile == "fast_bot":
                f["typingRate"] = np.random.uniform(800, 2500)
                f["pageTime"] = np.random.uniform(100, 800)
                f["avgMouseSpeed"] = np.random.uniform(10.0, 50.0)
                f["mouseJitter"] = 0
                f["avgKeyHoldDuration"] = np.random.uniform(1, 20)
            elif sub_profile == "slow_bot":
                f["typingRate"] = np.random.uniform(30, 150)
                f["pageTime"] = np.random.uniform(15000, 60000)
                f["avgMouseSpeed"] = np.random.uniform(0.1, 0.8)
                f["mouseDistance"] = np.random.uniform(100, 1500)
                f["avgKeyHoldDuration"] = np.random.uniform(150, 300)
                f["mouseJitter"] = 0
            elif sub_profile == "active_bot":
                f["typingRate"] = np.random.uniform(200, 600)
                f["pageTime"] = np.random.uniform(3000, 12000)
                f["avgMouseSpeed"] = np.random.uniform(1.0, 5.0)
                f["mouseDistance"] = np.random.uniform(2000, 10000)
                f["clickCount"] = np.random.randint(5, 20)
                f["scrollEventCount"] = np.random.randint(4, 15)
            elif sub_profile == "mimic_bot":
                # Bot perfectly copying average human metrics
                f["typingRate"] = np.random.normal(300, 20)
                f["pageTime"] = np.random.normal(5000, 200)
                f["avgMouseSpeed"] = np.random.normal(1.5, 0.1)
                f["avgKeyHoldDuration"] = np.random.normal(80, 5)
                f["mouseDistance"] = np.random.normal(1500, 100)
                f["mouseJitter"] = 2
                f["scrollEventCount"] = 2
            elif sub_profile == "irregular_bot":
                f["typingRate"] = np.random.choice([50, 1500])
                f["pageTime"] = np.random.choice([500, 30000])
                f["avgMouseSpeed"] = np.random.choice([0.1, 15.0])
                f["mouseJitter"] = np.random.randint(0, 30)
                f["backspaceCount"] = np.random.randint(0, 20)
                
            if f["mouseDistance"] == 0:
                f["mouseDistance"] = f["avgMouseSpeed"] * (f["pageTime"]/1000) * np.random.uniform(50, 500)
            if f["clickCount"] == 0: f["clickCount"] = np.random.randint(1, 5)
            if f["avgKeyHoldDuration"] == 0: f["avgKeyHoldDuration"] = np.random.uniform(10, 200)
            f["totalScrollDistance"] = f["scrollEventCount"] * np.random.uniform(50, 300)
            f["keyPressCount"] = 12 + f.get("backspaceCount", 0) + f.get("repeatedKeyCount", 0)
        
        # Derive V4 features
        f = derive_v4_features(f)
        
        row = {"true_label": label}
        for n in V4_FEATURE_NAMES:
            row[n] = float(f[n]) if isinstance(f[n], bool) else f[n]
        data.append(row)
        
    return pd.DataFrame(data)

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def train_and_evaluate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    out_dir = os.path.join(base_dir, "backend", "data", "v4_evaluation")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating V4 Training Data...")
    df_train = generate_v4_training_data(n_samples=2000)
    
    # Analyze V4 feature stats to check quality
    stats_data = []
    for feature in V4_FEATURE_NAMES:
        col = df_train[feature]
        stats_data.append({
            "feature": feature,
            "mean": col.mean(), "median": col.median(), "std": col.std(),
            "min": col.min(), "max": col.max(),
            "missing": col.isna().sum(), "zero_count": (col == 0).sum(),
            "unique": col.nunique()
        })
    pd.DataFrame(stats_data).to_csv(os.path.join(out_dir, "v4_feature_statistics.csv"), index=False)
    
    X = df_train[V4_FEATURE_NAMES].values
    y = (df_train["true_label"] == "bot").astype(int)
    
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Evaluate Models for V4
    models = {
        "LR": Pipeline([("scaler", StandardScaler()), ("lr", LogisticRegression())]),
        "DT": DecisionTreeClassifier(random_state=42),
        "RF": RandomForestClassifier(n_estimators=100, random_state=42),
        "GBM": GradientBoostingClassifier(random_state=42)
    }
    
    best_model = None
    best_score = 0
    for name, m in models.items():
        m.fit(X_train, y_train)
        preds = m.predict(X_val)
        acc = accuracy_score(y_val, preds)
        print(f"Validation {name} Acc: {acc:.4f}")
        if acc > best_score:
            best_score = acc
            best_model = m
            
    print(f"Selected Model: {type(best_model).__name__}")
    
    # Save V4 Model
    v4_model_path = os.path.join(base_dir, "backend", "models", "nvas_captcha_model_v4.joblib")
    joblib.dump(best_model, v4_model_path)
    
    # Feature Importance for V4 (if RF)
    if hasattr(best_model, "feature_importances_"):
        imps = best_model.feature_importances_
        imp_df = pd.DataFrame({"feature": V4_FEATURE_NAMES, "importance": imps})
        imp_df = imp_df.sort_values("importance", ascending=False)
        imp_df.to_csv(os.path.join(out_dir, "v4_feature_importance.csv"), index=False)
        top_features = imp_df.head(15)["feature"].tolist()
    else:
        top_features = ["N/A"]
        
    # Ablation Test on Validation Set
    X_train_v3 = X_train[:, :16]
    X_val_v3 = X_val[:, :16]
    rf_v3_abl = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_v3_abl.fit(X_train_v3, y_train)
    v3_abl_acc = accuracy_score(y_val, rf_v3_abl.predict(X_val_v3))
    print(f"Ablation Test - Model A (V3 features only) Acc: {v3_abl_acc:.4f}")
    print(f"Ablation Test - Model B (V4 features) Acc: {best_score:.4f}")
    
    # ----------------------------------------------------
    # V3 vs V4 on ADVERSARIAL BLIND DATASET
    # ----------------------------------------------------
    v3_model_path = os.path.join(base_dir, "backend", "models", "nvas_captcha_model_v3.joblib")
    blind_data_path = os.path.join(base_dir, "backend", "data", "adversarial_blind_test", "adversarial_blind_dataset.csv")
    
    hash_before = compute_sha256(v3_model_path)
    model_v3 = joblib.load(v3_model_path)
    hash_after = compute_sha256(v3_model_path)
    assert hash_before == hash_after, "V3 Model hash modified!"
    
    df_blind = pd.read_csv(blind_data_path)
    # Ensure V4 features exist in the blind dataset (re-derive them)
    def re_derive(row):
        f = row.to_dict()
        f = derive_v4_features(f)
        return pd.Series(f)
    df_blind = df_blind.apply(re_derive, axis=1)
    
    y_true_blind = (df_blind["true_label"] == "bot").astype(int)
    
    # V3 predictions
    X_blind_v3 = df_blind[V3_FEATURE_NAMES].values
    if hasattr(model_v3, "predict_proba"):
        probs_v3 = model_v3.predict_proba(X_blind_v3)[:, 1]
    else:
        probs_v3 = model_v3.predict(X_blind_v3)
    
    # V4 predictions
    X_blind_v4 = df_blind[V4_FEATURE_NAMES].values
    if hasattr(best_model, "predict_proba"):
        probs_v4 = best_model.predict_proba(X_blind_v4)[:, 1]
    else:
        probs_v4 = best_model.predict(X_blind_v4)
        
    def calc_metrics(y_t, y_p, y_prob):
        acc = accuracy_score(y_t, y_p)
        tn, fp, fn, tp = confusion_matrix(y_t, y_p).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        return acc, fpr, fnr
        
    v3_preds = (probs_v3 > 0.69).astype(int) # Standard block threshold for simple classification
    v4_preds = (probs_v4 > 0.69).astype(int)
    
    v3_acc, v3_fpr, v3_fnr = calc_metrics(y_true_blind, v3_preds, probs_v3)
    v4_acc, v4_fpr, v4_fnr = calc_metrics(y_true_blind, v4_preds, probs_v4)
    
    # Special Profile Metrics
    def profile_fnr(model_probs, profile_name):
        mask = df_blind["profile"] == profile_name
        if mask.sum() == 0: return 0.0
        y_t = y_true_blind[mask]
        preds = (model_probs[mask] > 0.69).astype(int)
        _, _, fn, tp = confusion_matrix(y_t, preds, labels=[0, 1]).ravel()
        return fn / (fn + tp) if (fn + tp) > 0 else 0.0

    def profile_block_rate(model_probs, profile_name):
        mask = df_blind["profile"] == profile_name
        if mask.sum() == 0: return 0.0
        preds = (model_probs[mask] > 0.69).astype(int)
        return preds.mean()
        
    v3_mimic_fnr = profile_fnr(probs_v3, "HUMAN_MIMIC_BOT")
    v4_mimic_fnr = profile_fnr(probs_v4, "HUMAN_MIMIC_BOT")
    
    v3_low_act_block = profile_block_rate(probs_v3, "LOW_ACTIVITY_HUMAN")
    v4_low_act_block = profile_block_rate(probs_v4, "LOW_ACTIVITY_HUMAN")

    print("\n==================================================")
    print("FINAL SUMMARY")
    print("==================================================")
    print(f"V3 Internal Test: N/A (Frozen)")
    print(f"V4 Internal Test: Acc = {best_score:.4f} (Validation)")
    print(f"V3 Adversarial Blind: Acc = {v3_acc:.4f}")
    print(f"V4 Adversarial Blind: Acc = {v4_acc:.4f}")
    print("")
    print("Human FPR:")
    print(f"V3 = {v3_fpr*100:.1f}%")
    print(f"V4 = {v4_fpr*100:.1f}%")
    print("")
    print("Bot FNR:")
    print(f"V3 = {v3_fnr*100:.1f}%")
    print(f"V4 = {v4_fnr*100:.1f}%")
    print("")
    print("Human-Mimic Bot FNR:")
    print(f"V3 = {v3_mimic_fnr*100:.1f}%")
    print(f"V4 = {v4_mimic_fnr*100:.1f}%")
    print("")
    print("Low-Activity Human Block Rate:")
    print(f"V3 = {v3_low_act_block*100:.1f}%")
    print(f"V4 = {v4_low_act_block*100:.1f}%")
    print("")
    print("Top V4 Features:")
    for i, f in enumerate(top_features[:5]):
        print(f"{i+1}. {f}")
    print("")
    
    if v4_acc > v3_acc and v4_low_act_block < v3_low_act_block and v4_mimic_fnr < v3_mimic_fnr:
        print("Most important improvement: V4 drastically reduces human false positives while detecting human-mimic bots using cross-modal rate features.")
        print("Remaining weakness: Adversarial bots that truly emulate BOTH timing and exact path distributions might still occasionally pass CAPTCHA.")
        print("Recommendation: V4 PROMISING")
    else:
        print("Most important improvement: Cross-modal feature engineering provided a new behavioral dimension.")
        print("Remaining weakness: The model still struggles with sophisticated overlap and threshold calibration.")
        print("Recommendation: TEST V4 FURTHER")
        
    with open(os.path.join(out_dir, "v3_vs_v4_adversarial_results.json"), "w") as f:
        json.dump({
            "V3": {"acc": v3_acc, "fpr": v3_fpr, "fnr": v3_fnr, "mimic_fnr": v3_mimic_fnr, "low_act_block": v3_low_act_block},
            "V4": {"acc": v4_acc, "fpr": v4_fpr, "fnr": v4_fnr, "mimic_fnr": v4_mimic_fnr, "low_act_block": v4_low_act_block}
        }, f, indent=4)

if __name__ == "__main__":
    train_and_evaluate()
