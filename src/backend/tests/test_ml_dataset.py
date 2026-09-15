"""
tests/test_ml_dataset.py — Unit tests for Phase 4 dataset loading and splitting.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from ml.feature_columns import FEATURE_COLUMNS, TARGET_COLUMN, TIMESTAMP_COLUMN


def test_feature_columns_non_empty():
    assert len(FEATURE_COLUMNS) > 0


def test_target_column_defined():
    assert TARGET_COLUMN == "future_congestion_risk_6h"


def test_load_all_data_returns_dataframe():
    from ml.dataset import load_all_data
    df = load_all_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert TIMESTAMP_COLUMN in df.columns


def test_validate_data_drops_nan():
    from ml.dataset import validate_data
    import numpy as np

    # Build a valid dataframe
    data = {col: [1.0, np.nan] for col in FEATURE_COLUMNS}
    data[TIMESTAMP_COLUMN] = pd.to_datetime(["2026-01-01", "2026-01-02"])
    data[TARGET_COLUMN] = [0, 1]
    df = pd.DataFrame(data)

    result = validate_data(df)
    assert len(result) == 1  # NaN row dropped


def test_chronological_split_sizes():
    from ml.dataset import chronological_split, load_all_data, validate_data
    df = load_all_data()
    df = validate_data(df)
    split = chronological_split(df)

    total = len(split.X_train) + len(split.X_val) + len(split.X_test)
    assert total == len(df)
    assert len(split.X_train) > len(split.X_val)
    assert len(split.X_val) > 0
    assert len(split.X_test) > 0


def test_no_future_leakage_in_features():
    """Ensure congestion_history columns are NOT in FEATURE_COLUMNS."""
    leaky_cols = [
        "future_congestion_index_6h",
        "future_congestion_risk_6h",
        "target_horizon_h",
    ]
    for col in leaky_cols:
        assert col not in FEATURE_COLUMNS, f"Leaky column in features: {col}"
