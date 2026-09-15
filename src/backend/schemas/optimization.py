"""
Pydantic schemas for optimization, comparison, scenarios, and 72h planning.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Optimization
# ---------------------------------------------------------------------------


class RunOptimizationRequest(BaseModel):
    time_limit_seconds: float = Field(default=10.0, ge=1.0, le=60.0)


class VesselAssignment(BaseModel):
    vessel_id: str
    vessel_name: str
    berth_id: str | None = None
    berth_name: str | None = None
    planned_start_h: float | None = None
    planned_end_h: float | None = None
    waiting_time_h: float | None = None
    handling_duration_h: float | None = None
    reason: str | None = None


class OptimizationResponse(BaseModel):
    solver_status: str
    solve_time_ms: float = 0.0
    objective_value: float = 0.0
    assignments: list[VesselAssignment] = []
    total_waiting_time_h: float = 0.0
    average_waiting_time_h: float = 0.0
    max_delay_h: float = 0.0
    explanation: list[str] = []


# ---------------------------------------------------------------------------
# Crane Allocation
# ---------------------------------------------------------------------------


class CraneAssignmentResponse(BaseModel):
    vessel_id: str
    vessel_name: str
    berth_id: str
    crane_ids: list[str] = []
    crane_names: list[str] = []
    total_rate: float = 0.0
    expected_handling_h: float = 0.0
    explanation: str = ""


# ---------------------------------------------------------------------------
# Route Optimization
# ---------------------------------------------------------------------------


class RouteRecommendationRequest(BaseModel):
    vessel_id: str


class RouteAlternative(BaseModel):
    route_id: str
    route_name: str
    score: float
    travel_time_h: float
    congestion: float
    risk: float


class RouteRecommendationResponse(BaseModel):
    vessel_id: str
    vessel_name: str
    recommended_route_id: str
    recommended_route_name: str
    estimated_travel_time_h: float
    congestion_score: float
    risk_score: float
    alternatives: list[RouteAlternative] = []
    reason: str = ""


# ---------------------------------------------------------------------------
# Plan Comparison
# ---------------------------------------------------------------------------


class PlanMetricsSchema(BaseModel):
    total_waiting_time_h: float = 0.0
    average_waiting_time_h: float = 0.0
    max_delay_h: float = 0.0
    berth_utilization: float = 0.0
    crane_utilization: float = 0.0
    yard_utilization: float = 0.0
    vessel_count: int = 0
    assigned_count: int = 0
    conflicts: int = 0
    throughput_vessels: int = 0
    congestion_score: float = 0.0


class ComparisonResponse(BaseModel):
    baseline: PlanMetricsSchema
    optimized: PlanMetricsSchema
    improvements: dict = {}
    explanation: list[str] = []


# ---------------------------------------------------------------------------
# What-If Scenarios
# ---------------------------------------------------------------------------


class ScenarioRequest(BaseModel):
    scenario_type: str = Field(..., pattern="^(vessel_delay|berth_unavailable)$")
    target_id: str
    parameters: dict = {}


class ScenarioResponse(BaseModel):
    scenario_name: str
    scenario_type: str
    baseline_result: dict = {}
    scenario_result: dict = {}
    comparison: dict = {}
    affected_vessels: list[str] = []
    impact_summary: list[str] = []


# ---------------------------------------------------------------------------
# 72-Hour Planning
# ---------------------------------------------------------------------------


class PlanningWindowSchema(BaseModel):
    label: str
    start_h: float
    end_h: float
    vessel_arrivals: int = 0
    vessel_names: list[str] = []
    expected_containers: int = 0
    berth_utilization: float = 0.0
    crane_utilization: float = 0.0
    yard_utilization: float = 0.0
    congestion_risk: str = "LOW"
    congestion_probability: float = 0.0
    expected_waiting_h: float = 0.0
    recommendations: list[str] = []


class Plan72HResponse(BaseModel):
    generated_at: str
    simulation_time: str
    windows: list[PlanningWindowSchema] = []
    summary: str = ""
    total_arrivals: int = 0
    peak_window: str = ""
