from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import health, verify

app = FastAPI(
    title="nvasCAPTCHA API",
    description="Backend API for NVAS CAPTCHA behavior verification",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  # Explicit origins required when allow_credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health.router)
app.include_router(verify.router)
