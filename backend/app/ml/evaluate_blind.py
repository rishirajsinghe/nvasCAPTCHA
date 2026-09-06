import os
import sys
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from data_generation.bootstrap_data import generate_human_features, generate_bot_features
from app.ml.feature_schema import extract_feature_list

def generate_blind_dataset(samples_per_category=200):
    categories = [
        ("human", "human"),
        ("bot", "scripted_delay"), # Normal automation
        ("bot", "fast"),           # Fast bot
        ("bot", "repetitive"),     # Repetitive bot
        ("bot", "no_mouse"),       # No-mouse bot
        ("bot", "human_like")      # Human-like bot
    ]
    
    data = []
    
    for label, profile in categories:
        for _ in range(samples_per_category):
            if label == "human":
                features = generate_human_features()
                source = "Human"
            else:
                features = generate_bot_features(profile)
                if profile == "scripted_delay":
                    source = "Normal automation"
                elif profile == "fast":
                    source = "Fast bot"
                elif profile == "repetitive":
                    source = "Repetitive bot"
                elif profile == "no_mouse":
                    source = "No-mouse bot"
                elif profile == "human_like":
                    source = "Human-like bot"
            
            flat_features = extract_feature_list(features)
            
            row = {
                "source": source,
                "true_label": label
            }
            # Add features to row
            feature_names = [
                "avgMouseSpeed", "clickCount", "mouseDistance", "mouseJitter",
                "keyPressCount", "avgKeyHoldDuration", "typingRate", "backspaceCount",
                "repeatedKeyCount", "scrollEventCount", "totalScrollDistance",
                "scrollDirectionChanges", "pageTime", "fieldInteractionCount",
                "hasTouch", "screenArea"
            ]
            for i, name in enumerate(feature_names):
                row[name] = flat_features[i]
                
            data.append(row)
            
    return pd.DataFrame(data)

def evaluate_blind():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    model_path = os.path.join(base_dir, "backend", "models", "nvas_captcha_model_v3.joblib")
    
    print(f"Loading frozen model from: {model_path}")
    model = joblib.load(model_path)
    
    print("Generating NEW BLIND DATA...")
    df = generate_blind_dataset(samples_per_category=200)
    
    # Save the generated blind dataset to a CSV file
    data_dir = os.path.join(base_dir, "backend", "data")
    os.makedirs(data_dir, exist_ok=True)
    blind_dataset_path = os.path.join(data_dir, "dataset_blind.csv")
    df.to_csv(blind_dataset_path, index=False)
    print(f"Saved blind dataset to: {blind_dataset_path}")
    
    feature_cols = [
        "avgMouseSpeed", "clickCount", "mouseDistance", "mouseJitter",
        "keyPressCount", "avgKeyHoldDuration", "typingRate", "backspaceCount",
        "repeatedKeyCount", "scrollEventCount", "totalScrollDistance",
        "scrollDirectionChanges", "pageTime", "fieldInteractionCount",
        "hasTouch", "screenArea"
    ]
    
    X_blind = df[feature_cols]
    y_true = df["true_label"]
    sources = df["source"]
    
    print("Evaluating model...")
    y_pred_int = model.predict(X_blind.values)
    y_pred = ["bot" if p == 1 else "human" for p in y_pred_int]
    
    df["predicted"] = y_pred
    
    print("\n" + "="*50)
    print("BLIND DATASET EVALUATION RESULTS")
    print("="*50)
    
    overall_acc = accuracy_score(y_true, y_pred)
    print(f"\nOverall Accuracy: {overall_acc:.4f}")
    
    print("\nBreakdown by Profile:")
    print("-" * 50)
    
    for source in df["source"].unique():
        mask = df["source"] == source
        subset = df[mask]
        acc = accuracy_score(subset["true_label"], subset["predicted"])
        print(f"{source:<20}: {acc*100:>6.2f}% Accuracy ({len(subset)} samples)")
        
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred))

if __name__ == "__main__":
    evaluate_blind()
