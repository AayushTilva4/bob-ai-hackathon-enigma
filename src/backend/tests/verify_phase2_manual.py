"""
Manual verification script for HarborAI Phase 2 simulation engine.
Runs the step-by-step verification requested in requirement 35.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from httpx import ASGITransport, AsyncClient
from main import app


async def run_manual_verification():
    print("==================================================")
    print("HARBORAI PHASE 2 — MANUAL SIMULATION VERIFICATION")
    print("==================================================")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    ) as client:
        # 1. Health check
        print("\n[Step 1] Checking Health...")
        res_health = await client.get("/api/health")
        print(f"GET /api/health -> {res_health.status_code}: {res_health.text}")
        assert res_health.status_code == 200

        # 2. Reset simulation
        print("\n[Step 2] Resetting simulation (seed=42)...")
        res_reset = await client.post("/api/simulation/reset", json={"seed": 42})
        print(f"POST /api/simulation/reset -> {res_reset.status_code}")
        reset_data = res_reset.json()
        print(f"Initial Sim Time: {reset_data.get('simulation_time')}")
        print(f"Initial Congestion Risk: {reset_data.get('kpis', {}).get('congestion_risk')}")
        print(f"Initial Congestion Score: {reset_data.get('kpis', {}).get('congestion_score')}")

        # 3. Advance 1 hour
        print("\n[Step 3] Advancing simulation 1 hour...")
        res_adv1 = await client.post("/api/simulation/advance", json={"hours": 1.0})
        print(f"POST /api/simulation/advance (1h) -> {res_adv1.status_code}")
        adv1_data = res_adv1.json()
        print(f"Sim Time: {adv1_data.get('simulation_time')}")
        print(f"KPIs after 1h: Queue={adv1_data.get('kpis', {}).get('queue_length')}, Berth Util={adv1_data.get('kpis', {}).get('berth_utilization')}, Score={adv1_data.get('kpis', {}).get('congestion_score')}")

        # 4. Advance 6 hours
        print("\n[Step 4] Advancing simulation 6 hours...")
        res_adv6 = await client.post("/api/simulation/advance", json={"hours": 6.0})
        print(f"POST /api/simulation/advance (6h) -> {res_adv6.status_code}")
        adv6_data = res_adv6.json()
        print(f"Sim Time: {adv6_data.get('simulation_time')}")
        print(f"KPIs after 6h: Completed Vessels={adv6_data.get('kpis', {}).get('completed_vessels')}, Throughput={adv6_data.get('kpis', {}).get('throughput_teu')} TEU, Score={adv6_data.get('kpis', {}).get('congestion_score')}")

        # 5. Inspect state
        print("\n[Step 5] Inspecting Simulation State...")
        res_state = await client.get("/api/simulation/state")
        state_data = res_state.json()
        print(f"GET /api/simulation/state -> {res_state.status_code}")
        print(f"Vessels count: {len(state_data.get('vessels', []))}")
        for v in state_data.get("vessels", [])[:5]:
            print(f"  Vessel '{v['name']}': status={v['status']}, lat={v['lat']}, lng={v['lng']}, progress={v['route_progress']}")

        # 6. Inspect events
        print("\n[Step 6] Inspecting Events...")
        res_events = await client.get("/api/simulation/events?limit=8")
        events_data = res_events.json()
        print(f"GET /api/simulation/events -> {res_events.status_code}, total={events_data.get('total')}")
        for e in events_data.get("data", [])[:5]:
            print(f"  Event: [{e['simulation_time']}] {e['event_type']} (vessel_id={e.get('vessel_id')})")

        # 7. Inspect KPIs
        print("\n[Step 7] Inspecting KPIs...")
        res_kpis = await client.get("/api/simulation/kpis")
        kpis_data = res_kpis.json()
        print(f"GET /api/simulation/kpis -> {res_kpis.status_code}")
        print(json.dumps(kpis_data, indent=2))

        # 8. Advance another 24 hours
        print("\n[Step 8] Advancing simulation 24 hours...")
        res_adv24 = await client.post("/api/simulation/advance", json={"hours": 24.0})
        adv24_data = res_adv24.json()
        print(f"POST /api/simulation/advance (24h) -> {res_adv24.status_code}")
        print(f"Sim Time: {adv24_data.get('simulation_time')}")
        print(f"Final Completed Vessels: {adv24_data.get('kpis', {}).get('completed_vessels')}")
        print(f"Final Throughput: {adv24_data.get('kpis', {}).get('throughput_teu')} TEU")
        print(f"Final Average Waiting Time: {adv24_data.get('kpis', {}).get('average_waiting_time_h')} h")
        print(f"Final Congestion Score: {adv24_data.get('kpis', {}).get('congestion_score')} ({adv24_data.get('kpis', {}).get('congestion_risk')})")

        print("\n==================================================")
        print("VERIFICATION COMPLETED SUCCESSFULLY!")
        print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_manual_verification())
