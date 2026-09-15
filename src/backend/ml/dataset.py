"""
dataset.py — Load and merge Phase 3 synthetic datasets for ML training.

Splitting strategy:
  Phase 3 generates congestion events concentrated in the first ~12 days
  of a 90-day simulation window.  A strict chronological split therefore
  puts ALL positive examples in the training partition, leaving val/test
  with no positive class — useless for evaluation.

  Since the data is SYNTHETIC (designed for ML benchmarking, not for
  real-time production forecasting), we use stratified random split
  (sklearn train_test_split with stratify=y, random_state=42).
  This guarantees both classes are present in every partition while
  keeping the split reproducible and the evaluation meaningful.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from ml.feature_columns import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    TIMESTAMP_COLUMN,
    TRAIN_RATIO,
    VAL_RATIO,
)

logger = logging.getLogger(__name__)

# Root of the datasets directory — navigates: ml/ -> backend/ -> src/ -> project root
_DATASETS_ROOT = Path(__file__).resolve().parents[3] / "datasets" / "synthetic"

SCENARIOS = ["normal", "congestion_stress", "demo"]

# Map string risk labels → binary int (LOW=0, MEDIUM/HIGH/CRITICAL=1)
_CONGESTED_LABELS = {"MEDIUM", "HIGH", "CRITICAL"}

RANDOM_STATE = 42


class DataSplit(NamedTuple):
    X_train: pd.DataFrame
    y_train: pd.Series
    X_val: pd.DataFrame
    y_val: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    timestamps_test: pd.Series


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_scenario(scenario_dir: Path) -> pd.DataFrame:
    """Load and merge operational + congestion CSVs for one scenario."""
    op_path = scenario_dir / "operational_history.csv"
    cong_path = scenario_dir / "congestion_history.csv"

    if not op_path.exists() or not cong_path.exists():
        logger.warning("Skipping %s — missing CSV files", scenario_dir.name)
        return pd.DataFrame()

    op_df = pd.read_csv(op_path, parse_dates=[TIMESTAMP_COLUMN])
    cong_df = pd.read_csv(cong_path, parse_dates=[TIMESTAMP_COLUMN])

    merged = pd.merge(
        op_df,
        cong_df[[TIMESTAMP_COLUMN, TARGET_COLUMN]],
        on=TIMESTAMP_COLUMN,
        how="inner",
    )
    merged["_scenario"] = scenario_dir.name
    return merged


def _binarise_target(df: pd.DataFrame) -> pd.DataFrame:
    """Convert string risk label to binary: LOW → 0, else → 1."""
    df = df.copy()
    raw = df[TARGET_COLUMN]
    if raw.dtype == object:
        df[TARGET_COLUMN] = raw.str.upper().isin(_CONGESTED_LABELS).astype(int)
    else:
        df[TARGET_COLUMN] = raw.astype(int)
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_all_data() -> pd.DataFrame:
    """Load and concatenate data from all available scenarios."""
    frames: list[pd.DataFrame] = []
    for scenario in SCENARIOS:
        scenario_dir = _DATASETS_ROOT / scenario
        if not scenario_dir.exists():
            logger.warning("Scenario directory not found: %s", scenario_dir)
            continue
        df = _load_scenario(scenario_dir)
        if not df.empty:
            frames.append(df)
            logger.info("Loaded scenario '%s': %d rows", scenario, len(df))

    if not frames:
        raise FileNotFoundError(
            f"No synthetic datasets found under {_DATASETS_ROOT}. "
            "Run Phase 3 pipeline first."
        )

    combined = pd.concat(frames, ignore_index=True)
    logger.info("Total rows after merge: %d", len(combined))
    return combined


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing values; binarise the target column."""
    before = len(df)
    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).copy()
    after = len(df)
    if before != after:
        logger.warning(
            "Dropped %d rows with NaN values (%.1f%%)",
            before - after,
            100 * (before - after) / before,
        )

    df = _binarise_target(df)
    label_dist = df[TARGET_COLUMN].value_counts().to_dict()
    logger.info("Binary target distribution: %s", label_dist)
    return df


def chronological_split(df: pd.DataFrame) -> DataSplit:
    """
    Stratified random split (70 / 15 / 15) with random_state=42.

    Phase 3 congestion events are concentrated in the first ~12 days of a
    90-day simulation, making a strict chronological split produce all-negative
    val/test sets.  Stratified split ensures both classes appear in every
    partition while keeping the evaluation reproducible.
    """
    y = df[TARGET_COLUMN]
    test_size = 1.0 - TRAIN_RATIO                         # 0.30
    val_relative = VAL_RATIO / (VAL_RATIO + (1.0 - TRAIN_RATIO - VAL_RATIO))  # 0.50 of 0.30

    # First cut: train vs (val+test)
    X_train_df, X_temp_df, y_train, y_temp = train_test_split(
        df, y,
        test_size=test_size,
        stratify=y,
        random_state=RANDOM_STATE,
    )
    # Second cut: val vs test (equal halves of the 30%)
    X_val_df, X_test_df, y_val, y_test = train_test_split(
        X_temp_df, y_temp,
        test_size=0.5,
        stratify=y_temp,
        random_state=RANDOM_STATE,
    )

    total = len(df)
    logger.info(
        "Stratified split — train: %d (%.0f%%) pos=%d | val: %d (%.0f%%) pos=%d | test: %d (%.0f%%) pos=%d",
        len(X_train_df), 100 * len(X_train_df) / total, int(y_train.sum()),
        len(X_val_df), 100 * len(X_val_df) / total, int(y_val.sum()),
        len(X_test_df), 100 * len(X_test_df) / total, int(y_test.sum()),
    )

    return DataSplit(
        X_train=X_train_df[FEATURE_COLUMNS].copy(),
        y_train=y_train.reset_index(drop=True),
        X_val=X_val_df[FEATURE_COLUMNS].copy(),
        y_val=y_val.reset_index(drop=True),
        X_test=X_test_df[FEATURE_COLUMNS].copy(),
        y_test=y_test.reset_index(drop=True),
        timestamps_test=X_test_df[TIMESTAMP_COLUMN].reset_index(drop=True),
    )


def get_class_weight_ratio(y_train: pd.Series) -> float:
    """Return scale_pos_weight for XGBoost (ratio of negative to positive samples)."""
    n_neg = int((y_train == 0).sum())
    n_pos = int((y_train == 1).sum())
    if n_pos == 0:
        logger.warning("No positive class in training set — check target generation")
        return 1.0
    ratio = n_neg / n_pos
    logger.info("Class ratio neg/pos = %.2f (scale_pos_weight)", ratio)
    return float(ratio)


def prepare_dataset() -> tuple[DataSplit, float]:
    """Full pipeline: load → validate → stratified split → compute class weight."""
    df = load_all_data()
    df = validate_data(df)
    split = chronological_split(df)
    scale_pos_weight = get_class_weight_ratio(split.y_train)
    return split, scale_pos_weight
