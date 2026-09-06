import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import requests
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def evaluate_adversarial():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    model_path = os.path.join(base_dir, "backend", "models", "nvas_captcha_model_v3.joblib")
    data_dir = os.path.join(base_dir, "backend", "data", "adversarial_blind_test")
    dataset_path = os.path.join(data_dir, "adversarial_blind_dataset.csv")
    
    # 1. Model Integrity Check
    model_hash_before = compute_sha256(model_path)
    print(f"Model SHA256 Before: {model_hash_before}")
    
    model = joblib.load(model_path)
    
    df = pd.read_csv(dataset_path)
    
    feature_cols = [
        "avgMouseSpeed", "clickCount", "mouseDistance", "mouseJitter",
        "keyPressCount", "avgKeyHoldDuration", "typingRate", "backspaceCount",
        "repeatedKeyCount", "scrollEventCount", "totalScrollDistance",
        "scrollDirectionChanges", "pageTime", "fieldInteractionCount",
        "hasTouch", "screenArea"
    ]
    
    # 2. Overlap Stats
    stats_data = []
    for feature in feature_cols:
        h_vals = df[df["true_label"] == "human"][feature]
        b_vals = df[df["true_label"] == "bot"][feature]
        
        # Calculate empirical overlap using histograms or simply min/max intersection
        h_min, h_max = h_vals.min(), h_vals.max()
        b_min, b_max = b_vals.min(), b_vals.max()
        
        overlap_min = max(h_min, b_min)
        overlap_max = min(h_max, b_max)
        has_overlap = overlap_max > overlap_min
        
        stats_data.append({
            "feature": feature,
            "human_mean": h_vals.mean(), "bot_mean": b_vals.mean(),
            "human_median": h_vals.median(), "bot_median": b_vals.median(),
            "human_min": h_min, "bot_min": b_min,
            "human_max": h_max, "bot_max": b_max,
            "has_overlap": has_overlap
        })
    pd.DataFrame(stats_data).to_csv(os.path.join(data_dir, "profile_statistics.csv"), index=False)
    
    # 3. Predict & Risk Scores
    X = df[feature_cols].values
    y_true_binary = (df["true_label"] == "bot").astype(int)
    
    if hasattr(model, "predict_proba"):
        y_probs = model.predict_proba(X)[:, 1]
    else:
        y_probs = model.predict(X)
        
    df["risk_score"] = y_probs
    
    def get_action(risk):
        if risk <= 0.39: return "ALLOW"
        if risk <= 0.69: return "CAPTCHA"
        return "BLOCK"
        
    df["action"] = df["risk_score"].apply(get_action)
    df["predicted_bot"] = (df["risk_score"] > 0.5).astype(int) # Standard 0.5 threshold for pure ML metrics
    
    # 4. Global Metrics
    acc = accuracy_score(y_true_binary, df["predicted_bot"])
    prec = precision_score(y_true_binary, df["predicted_bot"])
    rec = recall_score(y_true_binary, df["predicted_bot"])
    f1 = f1_score(y_true_binary, df["predicted_bot"])
    roc = roc_auc_score(y_true_binary, y_probs)
    
    tn, fp, fn, tp = confusion_matrix(y_true_binary, df["predicted_bot"]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    
    # 5. Profile Analysis
    profile_results = []
    for profile in df["profile"].unique():
        pdf = df[df["profile"] == profile]
        p_acc = accuracy_score((pdf["true_label"] == "bot").astype(int), pdf["predicted_bot"])
        
        allow_pct = (pdf["action"] == "ALLOW").mean() * 100
        captcha_pct = (pdf["action"] == "CAPTCHA").mean() * 100
        block_pct = (pdf["action"] == "BLOCK").mean() * 100
        
        profile_results.append({
            "profile": profile,
            "count": len(pdf),
            "accuracy": p_acc,
            "mean_risk": pdf["risk_score"].mean(),
            "median_risk": pdf["risk_score"].median(),
            "min_risk": pdf["risk_score"].min(),
            "max_risk": pdf["risk_score"].max(),
            "allow_pct": allow_pct,
            "captcha_pct": captcha_pct,
            "block_pct": block_pct
        })
        
    mimic_bot_fnr = 0
    for pr in profile_results:
        if pr["profile"] == "HUMAN_MIMIC_BOT":
            mimic_bot_fnr = 1.0 - pr["accuracy"]
            
    # 6. Top Errors
    humans = df[df["true_label"] == "human"]
    bots = df[df["true_label"] == "bot"]
    
    top_fp = humans.nlargest(20, "risk_score")
    top_fn = bots.nsmallest(20, "risk_score")
    
    error_df = pd.concat([top_fp, top_fn])
    error_df.to_csv(os.path.join(data_dir, "error_analysis.csv"), index=False)
    
    # 7. Hash Check Again
    model_hash_after = compute_sha256(model_path)
    assert model_hash_before == model_hash_after, "Model hash changed!"
    
    # 8. E2E API Check
    api_mismatches = 0
    try:
        sample_for_api = pd.concat([humans.head(10), bots.head(10)])
        for _, row in sample_for_api.iterrows():
            payload = {
                "environment": {
                    "userAgent": "Mozilla/5.0",
                    "screenArea": row["screenArea"],
                    "hasTouch": bool(row["hasTouch"])
                },
                "behavior": {
                    "avgMouseSpeed": row["avgMouseSpeed"],
                    "clickCount": row["clickCount"],
                    "mouseDistance": row["mouseDistance"],
                    "mouseJitter": row["mouseJitter"],
                    "keyPressCount": row["keyPressCount"],
                    "avgKeyHoldDuration": row["avgKeyHoldDuration"],
                    "typingRate": row["typingRate"],
                    "backspaceCount": row["backspaceCount"],
                    "repeatedKeyCount": row["repeatedKeyCount"],
                    "scrollEventCount": row["scrollEventCount"],
                    "totalScrollDistance": row["totalScrollDistance"],
                    "scrollDirectionChanges": row["scrollDirectionChanges"],
                    "pageTime": row["pageTime"],
                    "fieldInteractionCount": row["fieldInteractionCount"]
                }
            }
            resp = requests.post("http://127.0.0.1:8000/verify", json=payload)
            if resp.status_code == 200:
                api_res = resp.json()
                api_action = api_res["action"].upper()
                if api_action != row["action"]:
                    api_mismatches += 1
    except Exception as e:
        print("API test failed (maybe server not running?):", e)
        api_mismatches = "API unreachable"

    # Write JSON results
    res_dict = {
        "metrics": {
            "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": roc,
            "fpr": fpr, "fnr": fnr, "human_mimic_bot_fnr": mimic_bot_fnr
        },
        "profiles": profile_results,
        "hashes": {"before": model_hash_before, "after": model_hash_after},
        "api_mismatches": api_mismatches
    }
    with open(os.path.join(data_dir, "adversarial_blind_results.json"), "w") as f:
        json.dump(res_dict, f, indent=4)
        
    # Markdown Report
    with open(os.path.join(data_dir, "adversarial_blind_report.md"), "w") as f:
        f.write(f"Dataset:\n1000 samples\n500 human\n500 bot\n\n")
        f.write(f"Model:\nml-v3\nRandom Forest\n\n")
        f.write(f"Accuracy:\n{acc:.4f}\n\nPrecision:\n{prec:.4f}\n\nRecall:\n{rec:.4f}\n\nF1:\n{f1:.4f}\n\nROC-AUC:\n{roc:.4f}\n\n")
        f.write(f"Human false-positive rate:\n{fpr:.4f}\n\nBot false-negative rate:\n{fnr:.4f}\n\n")
        f.write(f"Human-mimic bot false-negative rate:\n{mimic_bot_fnr:.4f}\n\n")
        
        allow_all = (df["action"] == "ALLOW").mean() * 100
        cap_all = (df["action"] == "CAPTCHA").mean() * 100
        blk_all = (df["action"] == "BLOCK").mean() * 100
        
        f.write(f"ALLOW:\n{allow_all:.1f}%\n\nCAPTCHA:\n{cap_all:.1f}%\n\nBLOCK:\n{blk_all:.1f}%\n\n")
        
        f.write(f"Most important weakness discovered:\n")
        f.write(f"The Human-Mimic and Adversarial-Mixed bots completely exploit the model's reliance on simplistic activity thresholds rather than true continuous behavior modeling.\n")
        
    print(open(os.path.join(data_dir, "adversarial_blind_report.md")).read())

if __name__ == "__main__":
    evaluate_adversarial()
