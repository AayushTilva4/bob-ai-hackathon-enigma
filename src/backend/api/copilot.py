"""
api/copilot.py — AI Operations Copilot REST endpoints.

POST /api/copilot/chat    — Chat with the copilot (tool-based responses)
GET  /api/copilot/brief   — Get AI-generated operations brief
GET  /api/copilot/tools   — List available tools
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ai.brief import generate_operations_brief
from ai.tools import (
    TOOL_DEFINITIONS,
    get_berth_status,
    get_congestion_forecast,
    get_crane_status,
    get_port_status,
    get_vessel_status,
)
from database.connection import get_db
from database.models import Vessel, VesselStatus
from simulation.engine import simulation_engine
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/copilot", tags=["AI Copilot"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[dict] = []
    data: dict = {}
    grounded: bool = True


# ---------------------------------------------------------------------------
# Intent detection + tool routing (local, no LLM required)
# ---------------------------------------------------------------------------


_INTENT_PATTERNS: list[tuple[str, str, dict]] = [
    (r"(congestion|risk|forecast|predict)", "get_congestion_forecast", {}),
    (r"(port status|port state|overview|dashboard|kpi)", "get_port_status", {}),
    (r"(berth|dock|quay)\s*(status|avail|free|occupi)", "get_berth_status", {}),
    (r"(crane|gantry)\s*(status|avail|assign)", "get_crane_status", {}),
    (r"(vessel|ship)\s*(status|where|which|list)", "get_vessel_status", {}),
    (r"(horizon|pacific|atlantic|northern|southern|eastern|silver|golden|coral|blue|island|titan)",
     "get_vessel_status", {}),
    (r"(brief|summary|report|situation)", "get_brief", {}),
    (r"(optim|assign|schedule|plan|berth assign)", "optimization_info", {}),
    (r"(what.if|scenario|late|delay|unavail)", "scenario_info", {}),
    (r"(waiting|queue|wait time)", "get_congestion_forecast", {}),
]


def _detect_intent(message: str) -> tuple[str, dict]:
    """Simple pattern-based intent detection for the local copilot fallback."""
    msg_lower = message.lower()
    for pattern, tool_name, extra in _INTENT_PATTERNS:
        if re.search(pattern, msg_lower):
            # Extract vessel name if mentioned
            params = dict(extra)
            if tool_name == "get_vessel_status":
                # Try to extract vessel name
                vessel_names = ["horizon", "pacific", "atlantic", "northern", "southern",
                                "eastern", "silver", "golden", "coral", "blue", "island", "titan"]
                for name in vessel_names:
                    if name in msg_lower:
                        params["vessel_name"] = name
                        break
            return tool_name, params
    return "get_port_status", {}


async def _execute_tool(tool_name: str, params: dict, db: AsyncSession) -> dict[str, Any]:
    """Execute a tool function and return its result."""
    if tool_name == "get_port_status":
        return await get_port_status(db)
    elif tool_name == "get_vessel_status":
        return await get_vessel_status(db, vessel_name=params.get("vessel_name"))
    elif tool_name == "get_berth_status":
        return await get_berth_status(db)
    elif tool_name == "get_crane_status":
        return await get_crane_status(db)
    elif tool_name == "get_congestion_forecast":
        return await get_congestion_forecast(db)
    elif tool_name == "get_brief":
        return {"redirect": "brief"}
    elif tool_name == "optimization_info":
        return {"message": "Use the Optimization page to run OR-Tools berth assignment. POST /api/optimization/run to execute."}
    elif tool_name == "scenario_info":
        return {"message": "Use POST /api/optimization/scenario to simulate what-if scenarios like vessel delays or berth unavailability."}
    return {}


def _format_response(tool_name: str, data: dict, user_message: str) -> str:
    """Format tool result into a natural language response grounded in data."""
    if tool_name == "get_port_status":
        risk = data.get("congestion_risk", "unknown").upper()
        score = data.get("congestion_score", 0.0)
        berth = data.get("berth_utilization", 0.0)
        crane = data.get("crane_utilization", 0.0)
        yard = data.get("yard_utilization", 0.0)
        waiting = data.get("waiting_vessels", 0)
        active = data.get("active_vessels", 0)
        return (
            f"**Port Status Overview**\n\n"
            f"• Congestion Risk: **{risk}** (score: {score:.2f})\n"
            f"• Berth Utilization: **{berth:.0%}** ({data.get('occupied_berths', 0)} occupied, {data.get('available_berths', 0)} available)\n"
            f"• Crane Utilization: **{crane:.0%}** ({data.get('active_cranes', 0)} active)\n"
            f"• Yard Utilization: **{yard:.0%}**\n"
            f"• Active Vessels: **{active}** | Waiting: **{waiting}**\n"
            f"• Throughput: **{data.get('throughput_teu', 0)} TEU**"
        )

    elif tool_name == "get_vessel_status":
        vessels = data.get("vessels", [])
        if not vessels:
            return "No vessels found matching your query."
        lines = ["**Vessel Status**\n"]
        for v in vessels[:5]:
            berth_info = f" → Berth {v.get('assigned_berth_id', 'none')[:8]}..." if v.get("assigned_berth_id") else ""
            lines.append(
                f"• **{v['name']}** — {v['status'].upper()} | "
                f"{v['type']} | {v.get('length_m', 0):.0f}m | "
                f"Priority: {v.get('priority', 'normal')}{berth_info}"
            )
        return "\n".join(lines)

    elif tool_name == "get_berth_status":
        berths = data.get("berths", [])
        lines = ["**Berth Status**\n"]
        for b in berths:
            emoji = "🟢" if b["status"] == "available" else "🔴" if b["status"] == "occupied" else "🟡"
            lines.append(f"• {emoji} **{b['name']}** — {b['status'].upper()} (max: {b['max_vessel_length_m']:.0f}m / {b['max_draft_m']:.1f}m draft)")
        return "\n".join(lines)

    elif tool_name == "get_crane_status":
        cranes = data.get("cranes", [])
        lines = [f"**Crane Status** ({data.get('active', 0)} active, {data.get('available', 0)} available)\n"]
        for c in cranes:
            emoji = "⚙️" if c["status"] == "operating" else "✅" if c["status"] == "available" else "🔧"
            lines.append(f"• {emoji} **{c['name']}** — {c['status'].upper()} ({c['handling_rate']:.0f} containers/h)")
        return "\n".join(lines)

    elif tool_name == "get_congestion_forecast":
        risk = data.get("congestion_risk", "unknown").upper()
        score = data.get("congestion_score", 0.0)
        factors = []
        if data.get("berth_utilization", 0) > 0.6:
            factors.append(f"berth utilization at {data['berth_utilization']:.0%}")
        if data.get("waiting_vessels", 0) > 0:
            factors.append(f"{data['waiting_vessels']} vessel(s) waiting")
        if data.get("yard_utilization", 0) > 0.7:
            factors.append(f"yard at {data['yard_utilization']:.0%}")

        factor_str = ", ".join(factors) if factors else "all metrics within normal range"
        return (
            f"**Congestion Forecast**\n\n"
            f"• Risk Level: **{risk}** (score: {score:.2f})\n"
            f"• Contributing Factors: {factor_str}\n"
            f"• Queue Length: {data.get('queue_length', 0)} vessel(s)"
        )

    elif tool_name in ("optimization_info", "scenario_info"):
        return data.get("message", "Use the Optimization page for this action.")

    return "I've retrieved the requested data. See the attached tool output for details."


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/chat", response_model=ChatResponse, summary="Chat with AI copilot")
async def copilot_chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Process a natural language query using tool-based retrieval.
    The copilot identifies the intent, calls the appropriate tool,
    and formats a response grounded in real system data.
    """
    tool_name, params = _detect_intent(payload.message)

    # Handle brief redirect
    if tool_name == "get_brief":
        # Redirect to brief generation
        brief_data = await _generate_brief_data(db)
        return ChatResponse(
            reply=_format_brief(brief_data),
            tool_calls=[{"tool": "generate_operations_brief", "params": {}}],
            data=brief_data,
            grounded=True,
        )

    data = await _execute_tool(tool_name, params, db)
    reply = _format_response(tool_name, data, payload.message)

    return ChatResponse(
        reply=reply,
        tool_calls=[{"tool": tool_name, "params": params}],
        data=data,
        grounded=True,
    )


@router.get("/brief", summary="Get AI-generated operations brief")
async def get_operations_brief(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Generate a structured operations brief from current system state."""
    return await _generate_brief_data(db)


@router.get("/tools", summary="List available copilot tools")
async def list_tools() -> dict[str, Any]:
    """Return the list of tools the copilot can use."""
    return {"tools": TOOL_DEFINITIONS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _generate_brief_data(db: AsyncSession) -> dict[str, Any]:
    """Build operations brief from live data."""
    port_data = await get_port_status(db)
    vessel_data = await get_vessel_status(db)

    brief = generate_operations_brief(
        kpis=port_data,
        vessels=vessel_data.get("vessels", []),
        simulation_time=port_data.get("simulation_time", ""),
    )
    return brief


def _format_brief(brief: dict) -> str:
    """Format the operations brief as markdown text."""
    sections = brief.get("sections", {})
    lines = [f"**Operations Brief** — Risk: {brief.get('congestion_risk', 'N/A')}\n"]

    for title, items in sections.items():
        header = title.replace("_", " ").title()
        lines.append(f"\n**{header}:**")
        for item in items:
            lines.append(f"• {item}")

    return "\n".join(lines)
