# NVAS CAPTCHA — ML V3 Prototype

## 1. Objective
Build the ML V3 prototype for the hackathon demo by training on the existing synthetic baseline dataset. Prove that the model can be successfully loaded and queried through the FastAPI `/verify` endpoint without breaking existing workflows.

## 2. Dataset Source
**Synthetic Prototype Telemetry.**
Because real human NVAS telemetry has not yet been collected, this dataset consists entirely of generated behavioral sessions designed to mimic 8 bot profiles and human distributions.

## 3. Dataset Size
*   Total samples: 1000
*   Human samples: 500
*   Bot samples: 500

## 4. 16-Feature Schema
The dataset enforces the canonical 16-feature schema:
`avgMouseSpeed`, `clickCount`, `mouseDistance`, `mouseJitter`, `keyPressCount`, `avgKeyHoldDuration`, `typingRate`, `backspaceCount`, `repeatedKeyCount`, `scrollEventCount`, `totalScrollDistance`, `scrollDirectionChanges`, `pageTime`, `fieldInteractionCount`, `hasTouch`, `screenArea`

## 5. Train/Test Methodology
*   Split: 80% Train, 20% Holdout Test
*   Stratified by label to ensure class balance in the holdout
*   Random Seed: 42

## 6. Models Tested
1.  Logistic Regression
2.  Decision Tree
3.  Random Forest
4.  Gradient Boosting

## 7. Final Metrics (Holdout)
*   **Accuracy**: 99.50%
*   **Precision**: 99.01%
*   **Recall**: 100.0%
*   **F1 Score**: 99.50%
*   **ROC-AUC**: 99.81%

## 8. Selected Model
**Random Forest**. It achieved the highest cross-validation stability and near-perfect ROC-AUC on the holdout test. It correctly combines the 16 weak features to detect the deterministic synthetic rules used to generate the dataset.

## 9. Limitations
**V3 is currently a prototype trained on synthetic behavioral telemetry. Real human telemetry has not yet been collected, so the reported metrics should not be interpreted as production-world accuracy.**

The architecture is designed so real SDK telemetry can replace or supplement the synthetic training data later. Until then, these scores (e.g., 99.5% accuracy) simply indicate that the Random Forest successfully reverse-engineered the synthetic bot generation scripts.
