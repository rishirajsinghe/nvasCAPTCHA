# nvasCAPTCHA

A passive bot detection system that silently analyzes behavioral signals (mouse, keyboard, scroll) using ML — no puzzles, no friction for real users.

## How It Works

1. **JS SDK** — injected into the frontend, silently collects behavioral telemetry
2. **FastAPI Backend** — receives the payload and runs it through the ML model
3. **ML V4 (Random Forest)** — scores 22 behavioral features and returns a risk decision
4. **Decision Engine** — `ALLOW` (≤0.39) · `CAPTCHA` (0.40–0.69) · `BLOCK` (>0.69)

## Model Stats

Random Forest trained on 22 cross-modal behavioral features. Evaluated against an adversarial blind test set containing human-mimicking bots.

| Metric | V3 | V4 |
|---|---|---|
| Accuracy | 49.1% | **64.8%** |
| False Positive Rate | 22.2% | **2.2%** |
| False Negative Rate | 79.6% | **68.2%** |
| Human-Mimic Bot FNR | 100% | **28.0%** |

> Trained on synthetic behavioral data. Real-world accuracy will improve once genuine human telemetry is collected.

## Repo Structure

```
nvasCAPTCHA/
├── frontend/
│   ├── index.html          # Aadhaar-like UI mockup
│   ├── css/style.css
│   ├── js/app.js           # UI logic + NVAS SDK integration
│   └── test-bundle.js      # Pre-built JS SDK
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── ml/             # Model, feature schema, training scripts
│   │   ├── services/       # Verify, risk, and decision logic
│   │   ├── routes/         # /verify and /health endpoints
│   │   └── database/       # MongoDB audit logging
│   ├── models/             # .joblib model files (v4 active, v3 fallback)
│   ├── data/               # Evaluation results and adversarial test reports
│   ├── demo/               # Playwright bot and human demo scripts
│   └── requirements.txt
├── nvas-package/           # JS SDK source
│   └── src/
│       ├── behavior/       # Mouse, keyboard, scroll, interaction collectors
│       ├── features/       # Feature aggregator
│       └── api/            # HTTP client
└── docs/                   # ML evaluation and dataset documentation
```

## Setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --port 8000
```

**Frontend**
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500`

## Demo 

With both servers running:

```bash
# Bot — expects BLOCK
python backend/demo/adversarial_bot.py

# Human — expects ALLOW
python backend/demo/human_demo.py
```

> Requires Playwright: `playwright install chromium`

## API

`POST /verify` — send behavioral features, receive a risk score and decision.

`GET /health` — check API and model status.

## Stack

Python · FastAPI · scikit-learn · MongoDB · Vanilla JS · Playwright

---
*Hackathon prototype. The Aadhaar-like UI uses dummy data only and is not connected to any official service.*
