"""
preprocessing.py — Sklearn preprocessing pipeline for Phase 4 XGBoost model.

Uses StandardScaler for numeric features.
Saves/loads the fitted preprocessor alongside the model.
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.feature_columns import FEATURE_COLUMNS

logger = logging.getLogger(__name__)


def build_preprocessor() -> Pipeline:
    """Return an unfitted sklearn preprocessing pipeline."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
        ]
    )


def fit_preprocessor(pipeline: Pipeline, X_train: pd.DataFrame) -> Pipeline:
    """Fit the preprocessor on training data only."""
    pipeline.fit(X_train[FEATURE_COLUMNS])
    logger.info("Preprocessor fitted on %d training samples", len(X_train))
    return pipeline


def transform(pipeline: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Apply fitted preprocessor to a feature DataFrame."""
    return pipeline.transform(X[FEATURE_COLUMNS])


def save_preprocessor(pipeline: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    logger.info("Preprocessor saved to %s", path)


def load_preprocessor(path: Path) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError(f"Preprocessor not found at {path}. Train the model first.")
    pipeline = joblib.load(path)
    logger.info("Preprocessor loaded from %s", path)
    return pipeline
