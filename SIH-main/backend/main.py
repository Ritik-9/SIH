"""
main.py

FastAPI application entry point.

Run with:
    uvicorn backend.main:app --reload

Then open:
    http://127.0.0.1:8000/api/health
    http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend import weather_services, prediction_services
from backend.schemas import ForecastResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sih-heatwave-backend")

app = FastAPI(
    title="SIH Heatwave Prediction API",
    version="0.1.0",
)

# ------------------------------------------------------------
# CORS - allow local frontend dev servers to call this API
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Load ML models once, at startup - not per-request
# ------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    try:
        prediction_services.load_models()
        logger.info("Prediction models loaded successfully.")
    except prediction_services.ModelLoadError as exc:
        # Don't crash the server - /api/predict will report the problem
        # per-request instead of the whole API being unreachable.
        logger.error("Could not load prediction models: %s", exc)


# ------------------------------------------------------------
# Uniform error shape: {"error": "..."} for every failure mode
# ------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Invalid coordinates"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------
@app.get("/api/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


# ------------------------------------------------------------
# Main prediction endpoint
# ------------------------------------------------------------
@app.get("/api/predict", response_model=ForecastResponse)
def predict(
    latitude: float = Query(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    ),
    longitude: float = Query(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    ),
):
    if not prediction_services.models_ready():
        raise HTTPException(status_code=500, detail="Prediction models unavailable")

    try:
        hourly_df = weather_services.fetch_hourly_weather(latitude, longitude)
    except weather_services.WeatherServiceError as exc:
        logger.error("Weather service error: %s", exc)
        raise HTTPException(
            status_code=502, detail="Weather service temporarily unavailable"
        )

    try:
        result = prediction_services.build_forecast(latitude, longitude, hourly_df)
    except prediction_services.ModelLoadError as exc:
        logger.error("Prediction error: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction service unavailable")
    except Exception:
        logger.exception("Unexpected error during prediction")
        raise HTTPException(status_code=500, detail="Internal server error")

    return result