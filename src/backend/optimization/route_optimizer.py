"""
route_optimizer.py — Route scoring and recommendation.

Evaluates predefined simulated port approach routes based on
travel time, congestion, risk, and vessel compatibility.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RouteInfo:
    id: str
    name: str
    nominal_travel_time_h: float
    capacity: int
    congestion_factor: float
    risk_factor: float


@dataclass
class RouteRecommendation:
    vessel_id: str
    vessel_name: str
    recommended_route_id: str
    recommended_route_name: str
    estimated_travel_time_h: float
    congestion_score: float
    risk_score: float
    alternatives: list[dict]
    reason: str


def score_route(route: RouteInfo, vessel_draft_m: float = 0.0) -> float:
    """
    Score a route for desirability (lower is better).

    score = travel_time * (1 + congestion_factor) * (1 + risk_factor)
    """
    base = route.nominal_travel_time_h
    congestion_penalty = 1.0 + route.congestion_factor
    risk_penalty = 1.0 + route.risk_factor
    return round(base * congestion_penalty * risk_penalty, 3)


def recommend_routes(
    vessel_id: str,
    vessel_name: str,
    vessel_draft_m: float,
    routes: list[RouteInfo],
) -> RouteRecommendation:
    """
    Evaluate all routes and recommend the best one for a vessel.
    Returns the recommendation with alternatives and explanation.
    """
    if not routes:
        return RouteRecommendation(
            vessel_id=vessel_id,
            vessel_name=vessel_name,
            recommended_route_id="",
            recommended_route_name="None",
            estimated_travel_time_h=0.0,
            congestion_score=0.0,
            risk_score=0.0,
            alternatives=[],
            reason="No routes available",
        )

    scored = []
    for r in routes:
        s = score_route(r, vessel_draft_m)
        effective_travel = r.nominal_travel_time_h * (1 + r.congestion_factor)
        scored.append({
            "route_id": r.id,
            "route_name": r.name,
            "score": s,
            "travel_time_h": round(effective_travel, 2),
            "congestion": r.congestion_factor,
            "risk": r.risk_factor,
        })

    scored.sort(key=lambda x: x["score"])
    best = scored[0]

    # Build explanation
    reasons = [f"{best['route_name']} has lowest combined score ({best['score']:.2f})"]
    if best["congestion"] < 0.1:
        reasons.append("minimal congestion")
    if best["risk"] < 0.1:
        reasons.append("low navigational risk")
    if best["travel_time_h"] < 2.0:
        reasons.append(f"fast transit ({best['travel_time_h']:.1f}h)")

    return RouteRecommendation(
        vessel_id=vessel_id,
        vessel_name=vessel_name,
        recommended_route_id=best["route_id"],
        recommended_route_name=best["route_name"],
        estimated_travel_time_h=best["travel_time_h"],
        congestion_score=best["congestion"],
        risk_score=best["risk"],
        alternatives=scored[1:],
        reason="; ".join(reasons),
    )
