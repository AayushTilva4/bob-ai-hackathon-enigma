"""
inference.py — Real-time congestion prediction inference for Phase 4.

Loads the trained XGBoost model + preprocessor and runs predictions
on live port state data submitted via the API.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import numpy as np
import xgboost as xgb

from ml.feature_columns import FEATURE_COLUMNS
from ml.preprocessing import load_preprocessor
from ml.train import MODEL_PATH, PREPROCESSOR_PATH

logger = logging.getLogger(__name__)


class CongestionPredictor:
    """Singleton-style predictor that loads artifacts once and reuses them."""

    def __init__(self) -> None:
        self._model: xgb.XGBClassifier | None = None
        self._preprocessor = None
        self._loaded = False

    def load(self) -> None:
        """Load model and preprocessor from disk."""
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at {MODEL_PATH}. "
                "Run the training script first: python -m ml.train"
            )
        model = xgb.XGBClassifier()
        model.load_model(str(MODEL_PATH))
        self._model = model
        self._preprocessor = load_preprocessor(PREPROCESSOR_PATH)
        self._loaded = True
        logger.info("CongestionPredictor loaded from %s", MODEL_PATH)

    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, feature_dict: dict) -> dict:
        """
        Run prediction on a single observation.

        Parameters
        ----------
        feature_dict : dict
            Keys must include all FEATURE_COLUMNS.

        Returns
        -------
        dict with keys:
            congestion_risk_6h : int (0 or 1)
            congestion_probability : float (0.0–1.0)
            risk_level : str ("LOW", "MEDIUM", "HIGH")
            top_factors : list[dict]  — top contributing features
        """
        if not self._loaded:
            self.load()

        import pandas as pd  # lazy import

        row = {col: feature_dict.get(col, 0.0) for col in FEATURE_COLUMNS}
        X_df = pd.DataFrame([row])
        X_scaled = self._preprocessor.transform(X_df[FEATURE_COLUMNS])

        congestion_risk: int = int(self._model.predict(X_scaled)[0])
        congestion_prob: float = float(self._model.predict_proba(X_scaled)[0, 1])

        risk_level = _risk_level(congestion_prob)

        # Feature contributions (based on importances × feature values)
        importances = self._model.feature_importances_
        scaled_vals = X_scaled[0]
        contributions = np.abs(importances * scaled_vals)
        top_idx = np.argsort(contributions)[::-1][:5]
        top_factors = [
            {
                "feature": FEATURE_COLUMNS[i],
                "importance": float(importances[i]),
                "value": float(row[FEATURE_COLUMNS[i]]),
            }
            for i in top_idx
        ]

        return {
            "congestion_risk_6h": congestion_risk,
            "congestion_probability": round(congestion_prob, 4),
            "risk_level": risk_level,
            "top_factors": top_factors,
        }


def _risk_level(prob: float) -> str:
    if prob >= 0.65:
        return "HIGH"
    elif prob >= 0.40:
        return "MEDIUM"
    else:
        return "LOW"


# Module-level singleton
_predictor = CongestionPredictor()


def get_predictor() -> CongestionPredictor:
    """Return the global predictor instance (loads lazily on first call)."""
    if not _predictor.is_loaded():
        _predictor.load()
    return _predictor
