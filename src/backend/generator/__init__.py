"""
HarborAI Synthetic Dataset Generation Pipeline.

Phase 3 implementation:
- Deterministic synthetic generation of ports, berths, cranes, yard zones, routes, vessels, and containers
- 90 days of hourly weather and tide observations
- Simulation-based operational history generation
- Multi-factor congestion labels (no trivial single-rule targets)
- Data leakage prevention for ML training
- Scenarios: Normal, Congestion Stress, Demo
"""

from generator.scenario_config import (
    CongestionStressScenarioConfig,
    DemoScenarioConfig,
    NormalScenarioConfig,
    ScenarioConfig,
)

__all__ = [
    "ScenarioConfig",
    "NormalScenarioConfig",
    "CongestionStressScenarioConfig",
    "DemoScenarioConfig",
]
