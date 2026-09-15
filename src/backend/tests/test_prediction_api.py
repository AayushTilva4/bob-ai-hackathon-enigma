"""
tests/test_prediction_api.py — Phase 4 congestion prediction API tests.
Tests use a mock predictor to avoid requiring a trained model.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from main import app
    return TestClient(app)


SAMPLE_PAYLOAD = {
    "hour": 14,
    "day_of_week": 1,
    "day_of_month": 15,
    "month": 6,
    "is_weekend": 0,
    "active_vessel_count": 8,
    "waiting_vessel_count": 3,
    "queue_length": 3,
    "vessels_at_berth_count": 5,
    "high_priority_vessel_count": 1,
    "occupied_berths": 5,
    "available_berths": 3,
    "berth_utilization": 0.625,
    "active_cranes": 6,
    "available_cranes": 4,
    "crane_utilization": 0.60,
    "yard_occupancy": 8500,
    "yard_utilization": 0.73,
    "average_waiting_time_h": 4.2,
    "average_handling_time_h": 11.5,
    "scheduled_arrivals_next_6h": 4,
    "scheduled_arrivals_next_12h": 7,
    "scheduled_arrivals_next_24h": 15,
    "scheduled_incoming_containers_next_6h": 2200,
    "scheduled_incoming_containers_next_24h": 7800,
    "weather_temperature_c": 28.5,
    "weather_wind_speed_knots": 18.0,
    "weather_precipitation_mm": 0.0,
    "weather_operational_impact": 0.15,
    "tide_height_m": 4.8,
    "tide_operational_impact": 0.05,
    "current_throughput_teu": 1850.0,
}


def _mock_predictor():
    predictor = MagicMock()
    predictor.is_loaded.return_value = True
    predictor.predict.return_value = {
        "congestion_risk_6h": 1,
        "congestion_probability": 0.7832,
        "risk_level": "HIGH",
        "top_factors": [
            {"feature": "berth_utilization", "importance": 0.15, "value": 0.625},
            {"feature": "queue_length", "importance": 0.12, "value": 3.0},
            {"feature": "yard_utilization", "importance": 0.11, "value": 0.73},
            {"feature": "crane_utilization", "importance": 0.10, "value": 0.60},
            {"feature": "waiting_vessel_count", "importance": 0.09, "value": 3.0},
        ],
    }
    return predictor


def test_predict_congestion_returns_200(client):
    with patch("api.prediction.get_predictor", return_value=_mock_predictor()):
        resp = client.post("/api/prediction/congestion", json=SAMPLE_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert "congestion_risk_6h" in data
    assert "congestion_probability" in data
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert len(data["top_factors"]) == 5
    assert data["horizon_hours"] == 6


def test_predict_congestion_high_risk(client):
    with patch("api.prediction.get_predictor", return_value=_mock_predictor()):
        resp = client.post("/api/prediction/congestion", json=SAMPLE_PAYLOAD)
    data = resp.json()
    assert data["congestion_risk_6h"] == 1
    assert data["congestion_probability"] > 0.5
    assert data["risk_level"] == "HIGH"


def test_predict_congestion_missing_required_field(client):
    bad_payload = SAMPLE_PAYLOAD.copy()
    del bad_payload["hour"]
    resp = client.post("/api/prediction/congestion", json=bad_payload)
    assert resp.status_code == 422


def test_model_status_no_model(client, tmp_path, monkeypatch):
    monkeypatch.setattr("api.prediction.MODEL_PATH", tmp_path / "no_model.json")
    monkeypatch.setattr("api.prediction.METRICS_PATH", tmp_path / "no_metrics.json")
    resp = client.get("/api/prediction/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_loaded"] is False
    assert data["metrics_available"] is False


def test_trigger_training_returns_202(client):
    with patch("api.prediction._training_in_progress", False):
        with patch("ml.train.train", return_value={"test": {"auc_roc": 0.9}}):
            resp = client.post("/api/prediction/train")
    assert resp.status_code == 202
    assert resp.json()["status"] == "accepted"
