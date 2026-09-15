"""
Scenario configuration models for HarborAI Synthetic Dataset Generation.

Defines parameters for:
- NORMAL: balanced operations
- CONGESTION_STRESS: high-volume stress testing
- DEMO: controlled progression wave for hackathon demonstration
"""

from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    name: str
    seed: int = 42
    days: int = 90
    num_vessels: int = 60
    num_containers: int = 5500
    arrival_interval_min_h: float = 2.0
    arrival_interval_max_h: float = 5.0
    cluster_probability: float = 0.15
    weather_disruption_prob: float = 0.08
    tide_restriction_prob: float = 0.10
    avg_containers_per_vessel: int = 350
    target_horizon_hours: int = 6


class NormalScenarioConfig(ScenarioConfig):
    def __init__(self, seed: int = 42, days: int = 90, **kwargs) -> None:
        super().__init__(
            name="normal",
            seed=seed,
            days=days,
            num_vessels=kwargs.get("num_vessels", 60),
            num_containers=kwargs.get("num_containers", 5500),
            arrival_interval_min_h=2.5,
            arrival_interval_max_h=5.5,
            cluster_probability=0.10,
            weather_disruption_prob=0.05,
            tide_restriction_prob=0.05,
            avg_containers_per_vessel=300,
            target_horizon_hours=6,
        )


class CongestionStressScenarioConfig(ScenarioConfig):
    def __init__(self, seed: int = 42, days: int = 90, **kwargs) -> None:
        super().__init__(
            name="congestion_stress",
            seed=seed,
            days=days,
            num_vessels=kwargs.get("num_vessels", 75),
            num_containers=kwargs.get("num_containers", 7000),
            arrival_interval_min_h=1.0,
            arrival_interval_max_h=3.0,
            cluster_probability=0.45,
            weather_disruption_prob=0.20,
            tide_restriction_prob=0.18,
            avg_containers_per_vessel=480,
            target_horizon_hours=6,
        )


class DemoScenarioConfig(ScenarioConfig):
    def __init__(self, seed: int = 42, days: int = 90, **kwargs) -> None:
        super().__init__(
            name="demo",
            seed=seed,
            days=days,
            num_vessels=kwargs.get("num_vessels", 65),
            num_containers=kwargs.get("num_containers", 6000),
            arrival_interval_min_h=1.5,
            arrival_interval_max_h=4.0,
            cluster_probability=0.25,
            weather_disruption_prob=0.10,
            tide_restriction_prob=0.10,
            avg_containers_per_vessel=380,
            target_horizon_hours=6,
        )


def get_scenario_config(name: str, seed: int = 42, days: int = 90, **kwargs) -> ScenarioConfig:
    """Factory helper to obtain a ScenarioConfig by name."""
    clean_name = name.lower().strip()
    if clean_name in ("normal", "default"):
        return NormalScenarioConfig(seed=seed, days=days, **kwargs)
    elif clean_name in ("congestion_stress", "stress", "congested"):
        return CongestionStressScenarioConfig(seed=seed, days=days, **kwargs)
    elif clean_name in ("demo", "demonstration"):
        return DemoScenarioConfig(seed=seed, days=days, **kwargs)
    else:
        raise ValueError(f"Unknown scenario '{name}'. Supported: 'normal', 'congestion_stress', 'demo'.")
