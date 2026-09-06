# NVAS CAPTCHA Dataset Analysis

## 1. Dataset Overview

This document outlines the evaluation of several public behavioral biometrics datasets for potential integration into the NVAS CAPTCHA machine learning pipeline. The goal is to move from our perfectly separable (and artificial) synthetic bootstrap dataset to real-world human and bot behavioral data.

We investigated four major datasets:
1. **Bournemouth Web Bot Detection Dataset**
2. **Balabit Mouse Dynamics Challenge Dataset**
3. **CMU Keystroke Dynamics Benchmark Dataset**
4. **Mendeley Mouse Dynamics Datasets**

## 2. Official Sources & 3. Licenses

*   **Bournemouth Web Bot Detection Dataset**: 
    *   *Source*: BORDaR (Bournemouth Online Research Data Repository)
    *   *License*: Academic/Research (typically requires request/approval).
*   **Balabit Mouse Dynamics Challenge**:
    *   *Source*: `https://github.com/balabit/Mouse-Dynamics-Challenge`
    *   *License*: MIT / Academic Challenge rules.
*   **CMU Keystroke Dynamics Benchmark**:
    *   *Source*: `http://www.cs.cmu.edu/~keystroke/`
    *   *License*: Public Domain / Research Citation Required (Killourhy & Maxion).
*   **Mendeley Mouse Dynamics Dataset**:
    *   *Source*: `https://data.mendeley.com/`
    *   *License*: Various (CC BY 4.0 typically).

## 4. Download Status

*   **Bournemouth Web Bot**: `DOWNLOAD STATUS: MANUAL DOWNLOAD REQUIRED` (Requires navigating the BORDaR academic portal).
*   **Balabit Mouse Dynamics**: `DOWNLOAD STATUS: IN PROGRESS` (Cloning from GitHub to `backend/data/external/balabit`).
*   **CMU Keystroke Dynamics**: `DOWNLOAD STATUS: SUCCESSFULLY DOWNLOADED` (Downloaded `DSL-StrongPasswordData.csv` to `backend/data/external/cmu_keystroke/`).
*   **Mendeley Mouse Dynamics**: `DOWNLOAD STATUS: MANUAL DOWNLOAD REQUIRED` (Requires accepting Mendeley terms via web interface).

## 5. File Inventory & 6. Dataset Statistics

**CMU Keystroke Dynamics (`DSL-StrongPasswordData.csv`)**:
*   *Format*: CSV
*   *Size*: ~4.45 MB
*   *Records*: 20,400 rows (400 sessions × 51 subjects)
*   *Features*: 34 columns (Subject, sessionIndex, rep, and 31 timing columns)
*   *Labels*: Subject IDs (s002 to s057). No "Bot" labels; it is 100% human typists.

**Balabit Mouse Dynamics (Based on standard repo structure)**:
*   *Format*: CSV files per user
*   *Records*: Millions of coordinate events across 10 test users.
*   *Features*: `record timestamp`, `client timestamp`, `button`, `state`, `x`, `y`.
*   *Labels*: User IDs. No explicit "bot" labels.

## 7. Available Labels

*   **CMU Keystroke**: 100% Human (Multi-class User IDs). **No Bot Data**.
*   **Balabit Mouse**: 100% Human (Multi-class User IDs). **No Bot Data**.
*   *Observation*: Most public behavioral biometrics datasets are designed for *continuous authentication* (identifying User A vs User B), not *bot detection* (Human vs Bot).

## 8. NVAS Feature Compatibility

Our current ML pipeline requires a strict 16-feature vector. 

| Dataset | NVAS Feature | Directly Available | Derivable | Impossible | Conversion Needed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Balabit** | `avgMouseSpeed` | No | Yes | No | Calculate dist(x,y)/dt |
| **Balabit** | `clickCount` | No | Yes | No | Count `state` changes |
| **Balabit** | `mouseDistance` | No | Yes | No | Sum Euclidean dists |
| **Balabit** | `mouseJitter` | No | Yes | No | Calculate angle variance |
| **Balabit** | `keyPressCount` | No | No | **Impossible** | N/A |
| **Balabit** | `avgKeyHoldDuration` | No | No | **Impossible** | N/A |
| **CMU** | `keyPressCount` | No | Yes | No | Constant 11 (password length)|
| **CMU** | `avgKeyHoldDuration` | No | Yes | No | Average the `H.*` columns |
| **CMU** | `typingRate` | No | Yes | No | Calculate from total time |
| **CMU** | `backspaceCount` | No | No | **Impossible** | Clean traces only |
| **CMU** | `repeatedKeyCount` | No | No | **Impossible** | Clean traces only |
| **CMU/Balabit** | `scrollEventCount` | No | No | **Impossible** | N/A |
| **CMU/Balabit** | `pageTime` | No | Yes | No | Sum session time |
| **CMU/Balabit** | `hasTouch` | No | No | **Impossible** | N/A |
| **CMU/Balabit** | `screenArea` | No | No | **Impossible** | N/A |

## 9. Missing Features

No single external dataset can provide the complete 16-feature vector required by NVAS.
*   CMU lacks mouse, scroll, and environment data.
*   Balabit lacks keyboard, scroll, and environment data.

## 10. Conversion Requirements

**Balabit Converter (`balabit_parser.py`)**:
*   Read sequential `(x, y, t)` rows for a session.
*   Iterate through rows to compute Euclidean distance per tick.
*   Sum distance (`mouseDistance`), compute averages (`avgMouseSpeed`), and count direction reversals (`mouseJitter`).
*   Output partial vector. Pad keyboard/scroll features with `0.0`.

**CMU Converter (`cmu_parser.py`)**:
*   Read each row (one full session).
*   Extract the `H.period` columns. Average them to get `avgKeyHoldDuration`.
*   Sum all `H` and `UD` columns to get total session time.
*   Output partial vector. Pad mouse/scroll features with `0.0`.

## 11. Recommended Usage

*   **Direct Training?** **NO**. Because they lack 50%+ of the required NVAS features, training the Soft Voting Classifier on padded `0.0` data will destroy the model's ability to learn real keyboard/mouse correlations.
*   **Actual Usage**: These datasets should be used for **Feature Validation and Research**. We can use the CMU data to calculate the true real-world mean and standard deviation of `avgKeyHoldDuration` (e.g., humans hold keys for ~90-120ms). We then update our `bootstrap_data.py` generator to match these *real* statistical distributions.

## 12. Data Leakage Risks

If we were to train on these datasets, we would face severe leakage risks:
1.  **Imputation Leakage**: Padding missing features with `0.0` creates a massive artifact. The ML model will instantly learn that `avgMouseSpeed == 0.0` means "CMU Dataset", not "Bot".
2.  **Session Overlap**: CMU data contains 400 sessions from the *same* 51 users. A random 80/20 split will place the same user in both Train and Test sets, artificially inflating accuracy.

## 13. Privacy/Licensing Considerations

The CMU dataset requires explicit citation of Killourhy and Maxion (2009). It does not contain PII, as the users typed a standard benchmark password (`.tie5Roanl`).

## 14. Recommended Next Step

**Do not attempt to stitch Balabit and CMU data together to train the model.**

Instead, follow this Dataset Strategy:

1.  **Stage 1 (Complete)**: Synthetic data for pipeline mechanics (Accuracy = 1.00).
2.  **Stage 2 (Next)**: Analyze the CMU and Balabit data mathematically to find the *true* bounds of human behavior (e.g., max typing speed, real mouse jitter variance).
3.  **Stage 3**: Update `bot_generator.py` and `bootstrap_data.py` to use these scientifically backed boundaries. Generate a much harder, realistic synthetic dataset.
4.  **Stage 4**: Deploy the CAPTCHA to a live host website and collect *our own* complete 16-feature NVAS dataset. Only then should we retrain the final production ML model.
