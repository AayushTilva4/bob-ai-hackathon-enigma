"""
api/prediction.py — Congestion prediction REST endpoints for Phase 4.

POST /api/prediction/congestion  — predict congestion risk from current port state
GET  /api/prediction/status       — model load status and last known metrics
POST /api/prediction/train        — trigger model training (admin/dev endpoint)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ml.inference import CongestionPredictor, get_predictor
from ml.train import METRICS_PATH, MODEL_PATH
from schemas.prediction import (
    CongestionPredictionRequest,
    CongestionPredictionResponse,
    ModelStatusResponse,
    TopFactor,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/prediction", tags=["Congestion Prediction"])


@router.post(
    "/congestion",
    response_model=CongestionPredictionResponse,
    summary="Predict port congestion risk for next 6 hours",
)
async def predict_congestion(payload: CongestionPredictionRequest) -> CongestionPredictionResponse:
    """
    Accepts the current port operational snapshot and returns a congestion
    risk prediction for the next 6 hours using a trained XGBoost model.
    """
    try:
        predictor = get_predictor()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Model not trained yet. {exc}",
        ) from exc

    feature_dict = payload.model_dump()
    result = predictor.predict(feature_dict)

    return CongestionPredictionResponse(
        congestion_risk_6h=result["congestion_risk_6h"],
        congestion_probability=result["congestion_probability"],
        risk_level=result["risk_level"],
        top_factors=[TopFactor(**f) for f in result["top_factors"]],
        model_name="XGBoost Congestion Classifier",
        horizon_hours=6,
    )


@router.get(
    "/status",
    response_model=ModelStatusResponse,
    summary="Get ML model status and metrics",
)
async def model_status() -> ModelStatusResponse:
    """Returns whether the model is loaded and its last training metrics."""
    model_loaded = MODEL_PATH.exists()
    metrics_available = METRICS_PATH.exists()

    test_auc = test_f1 = test_acc = None
    if metrics_available:
        try:
            with open(METRICS_PATH) as f:
                m = json.load(f)
            test_auc = m.get("test", {}).get("auc_roc")
            test_f1 = m.get("test", {}).get("f1")
            test_acc = m.get("test", {}).get("accuracy")
        except Exception as exc:
            logger.warning("Could not read metrics file: %s", exc)

    return ModelStatusResponse(
        model_loaded=model_loaded,
        model_path=str(MODEL_PATH) if model_loaded else None,
        metrics_available=metrics_available,
        test_auc_roc=test_auc,
        test_f1=test_f1,
        test_accuracy=test_acc,
    )


_training_in_progress = False


@router.post(
    "/train",
    summary="Trigger model training (dev/admin)",
    status_code=202,
)
async def trigger_training(background_tasks: BackgroundTasks) -> dict:
    """
    Triggers model training as a background task.
    Returns 202 Accepted immediately.
    """
    global _training_in_progress
    if _training_in_progress:
        raise HTTPException(status_code=409, detail="Training already in progress.")

    def _run_training() -> None:
        global _training_in_progress
        _training_in_progress = True
        try:
            from ml.train import train
            metrics = train()
            logger.info("Background training complete. Test AUC: %.4f", metrics["test"]["auc_roc"])
        except Exception as exc:
            logger.error("Background training failed: %s", exc, exc_info=True)
        finally:
            _training_in_progress = False

    background_tasks.add_task(_run_training)
    return {"status": "accepted", "message": "Model training started in background."}
