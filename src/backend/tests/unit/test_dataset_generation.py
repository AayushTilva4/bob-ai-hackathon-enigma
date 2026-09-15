"""
Unit tests for the Phase 3 Synthetic Dataset Generation Pipeline.
"""

import json
from pathlib import Path

import pytest

from generator.pipeline import DatasetGenerationPipeline
from generator.scenario_config import (
    CongestionStressScenarioConfig,
    DemoScenarioConfig,
    NormalScenarioConfig,
    get_scenario_config,
)
from scripts.validate_dataset import validate_dataset


def test_scenario_config_factory():
    c_norm = get_scenario_config("normal", seed=42, days=30)
    assert c_norm.name == "normal"
    assert c_norm.days == 30
    assert c_norm.seed == 42

    c_stress = get_scenario_config("congestion_stress", seed=99)
    assert c_stress.name == "congestion_stress"
    assert c_stress.seed == 99

    c_demo = get_scenario_config("demo")
    assert c_demo.name == "demo"

    with pytest.raises(ValueError):
        get_scenario_config("invalid_scenario_name")


def test_dataset_generation_volume_and_integrity(tmp_path: Path):
    """Test generating a small scenario to verify volume, referential integrity, and files."""
    config = NormalScenarioConfig(seed=42, days=7, num_vessels=50, num_containers=5000)
    pipeline = DatasetGenerationPipeline(config)
    res = pipeline.run(tmp_path)

    assert res["vessels"] >= 50
    assert res["containers"] >= 5000
    assert res["operational_rows"] == 7 * 24
    assert res["weather_rows"] == 7 * 24
    assert res["tide_rows"] == 7 * 24
    assert res["congestion_rows"] == 7 * 24

    # Verify all files exist
    expected_files = [
        "ports.csv", "berths.csv", "cranes.csv", "yard_zones.csv", "routes.csv",
        "vessels.csv", "vessel_schedule.csv", "containers.csv", "weather.csv",
        "tides.csv", "operational_history.csv", "congestion_history.csv",
        "dataset_metadata.json"
    ]
    for fn in expected_files:
        assert (tmp_path / fn).exists(), f"Missing file: {fn}"

    # Verify metadata
    with open(tmp_path / "dataset_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
        assert meta["synthetic"] is True
        assert meta["seed"] == 42
        assert meta["primary_target"] == "future_congestion_risk_6h"


def test_deterministic_reproducibility(tmp_path: Path):
    """Running pipeline twice with same seed produces identical operational rows."""
    dir1 = tmp_path / "run1"
    dir2 = tmp_path / "run2"

    config1 = DemoScenarioConfig(seed=42, days=5, num_vessels=50, num_containers=5000)
    pipeline1 = DatasetGenerationPipeline(config1)
    pipeline1.run(dir1)

    config2 = DemoScenarioConfig(seed=42, days=5, num_vessels=50, num_containers=5000)
    pipeline2 = DatasetGenerationPipeline(config2)
    pipeline2.run(dir2)

    with open(dir1 / "operational_history.csv", "r", encoding="utf-8") as f1, \
         open(dir2 / "operational_history.csv", "r", encoding="utf-8") as f2:
        assert f1.read() == f2.read(), "operational_history.csv not reproducible!"

    with open(dir1 / "congestion_history.csv", "r", encoding="utf-8") as f1, \
         open(dir2 / "congestion_history.csv", "r", encoding="utf-8") as f2:
        assert f1.read() == f2.read(), "congestion_history.csv not reproducible!"


def test_validator_on_generated_dataset(tmp_path: Path):
    """Verify validator succeeds on valid output and fails on corrupt data."""
    config = NormalScenarioConfig(seed=42, days=90, num_vessels=50, num_containers=5000)
    pipeline = DatasetGenerationPipeline(config)
    pipeline.run(tmp_path)

    is_valid, errors, stats = validate_dataset(tmp_path)
    assert is_valid is True, f"Validation failed with errors: {errors}"
    assert stats["vessels_count"] >= 50
    assert stats["containers_count"] >= 5000
    assert len(stats["class_distribution"]) >= 2

    # Test corruption detection: remove a required file
    (tmp_path / "berths.csv").unlink()
    is_valid_corrupt, errors_corrupt, _ = validate_dataset(tmp_path)
    assert is_valid_corrupt is False
    assert any("berths.csv" in err for err in errors_corrupt)
