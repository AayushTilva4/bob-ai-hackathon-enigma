"""
train.py — XGBoost congestion classifier training for Phase 4.

Trains on Phase 3 synthetic data with chronological 70/15/15 split.
Saves model + preprocessor artifacts to models/ directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)

from ml.dataset import prepare_dataset
from ml.feature_columns import FEATURE_COLUMNS, TARGET_COLUMN
from ml.preprocessing import build_preprocessor, fit_preprocessor, save_preprocessor, transform

logger = logging.getLogger(__name__)

# Artifact paths — ml/ -> backend/ -> src/ -> project root -> models/
_MODELS_DIR = Path(__file__).resolve().parents[3] / "models"
MODEL_PATH = _MODELS_DIR / "congestion_xgb.json"
PREPROCESSOR_PATH = _MODELS_DIR / "preprocessor.joblib"
METRICS_PATH = _MODELS_DIR / "training_metrics.json"


def train() -> dict:
    """
    Full training pipeline:
    1. Load + validate + split data
    2. Fit preprocessor on train
    3. Train XGBoost classifier
    4. Evaluate on val + test
    5. Save model, preprocessor, metrics
    Returns training metrics dict.
    """
    logger.info("=== Phase 4: HarborAI Congestion Prediction Training ===")

    # 1. Data
    split, scale_pos_weight = prepare_dataset()

    # 2. Preprocess
    preprocessor = build_preprocessor()
    preprocessor = fit_preprocessor(preprocessor, split.X_train)

    X_train_np = transform(preprocessor, split.X_train)
    X_val_np = transform(preprocessor, split.X_val)
    X_test_np = transform(preprocessor, split.X_test)

    y_train = split.y_train.values
    y_val = split.y_val.values
    y_test = split.y_test.values

    # 3. Train XGBoost
    logger.info("Training XGBoost classifier...")
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=20,
    )

    model.fit(
        X_train_np, y_train,
        eval_set=[(X_val_np, y_val)],
        verbose=False,
    )

    best_iter = model.best_iteration
    logger.info("Best iteration: %d", best_iter)

    # 4. Evaluate
    def evaluate_split(X_np: np.ndarray, y_true: np.ndarray, name: str) -> dict:
        y_pred = model.predict(X_np)
        y_prob = model.predict_proba(X_np)[:, 1]
        acc = float(accuracy_score(y_true, y_pred))
        f1 = float(f1_score(y_true, y_pred, zero_division=0, labels=[1], average="binary"))
        try:
            auc = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            # Only one class present in this split (common with chronological ordering)
            auc = 0.0
        report = classification_report(
            y_true, y_pred,
            labels=[0, 1],
            target_names=["No Congestion", "Congestion"],
            output_dict=True,
            zero_division=0,
        )
        logger.info(
            "%s — Accuracy: %.4f | F1: %.4f | AUC-ROC: %.4f",
            name, acc, f1, auc,
        )
        return {"accuracy": acc, "f1": f1, "auc_roc": auc, "report": report}

    val_metrics = evaluate_split(X_val_np, y_val, "Validation")
    test_metrics = evaluate_split(X_test_np, y_test, "Test")

    # Feature importance (top 10)
    importance = dict(zip(FEATURE_COLUMNS, model.feature_importances_.tolist()))
    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
    logger.info("Top features: %s", top_features)

    metrics = {
        "model": "XGBoost Congestion Classifier",
        "target": TARGET_COLUMN,
        "best_iteration": best_iter,
        "train_samples": int(len(y_train)),
        "val_samples": int(len(y_val)),
        "test_samples": int(len(y_test)),
        "scale_pos_weight": float(scale_pos_weight),
        "validation": val_metrics,
        "test": test_metrics,
        "top_features": dict(top_features),
    }

    # 5. Save artifacts
    _MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    save_preprocessor(preprocessor, PREPROCESSOR_PATH)

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Model saved to %s", MODEL_PATH)
    logger.info("Metrics saved to %s", METRICS_PATH)
    logger.info("=== Training complete ===")

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    results = train()
    print(f"\nValidation AUC-ROC: {results['validation']['auc_roc']:.4f}")
    print(f"Test AUC-ROC:       {results['test']['auc_roc']:.4f}")
    print(f"Test F1:            {results['test']['f1']:.4f}")
    print(f"Test Accuracy:      {results['test']['accuracy']:.4f}")
