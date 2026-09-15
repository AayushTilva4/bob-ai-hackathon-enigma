"""
Dataset import utility for HarborAI.

Optionally imports a validated synthetic dataset scenario into PostgreSQL in
dependency order (Berths, Cranes, YardZones, Routes, Vessels, Schedules).

Usage:
  python -m scripts.import_dataset datasets/synthetic/demo/ [--dry-run]
"""

import argparse
import asyncio
import csv
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select

from database.connection import AsyncSessionLocal
from database.models import (
    Berth,
    BerthStatus,
    Crane,
    CraneStatus,
    Route,
    Schedule,
    ScheduleStatus,
    Vessel,
    VesselPriority,
    VesselStatus,
    VesselType,
    YardZone,
)
from scripts.validate_dataset import validate_dataset


def _load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


async def import_dataset(dataset_dir: Path, dry_run: bool = False) -> None:
    print("==================================================")
    print(f"HARBORAI DATASET IMPORTER")
    print(f"Directory: {dataset_dir}")
    print(f"Dry run:   {dry_run}")
    print("==================================================")

    # 1. Validate dataset first
    is_valid, errors, stats = validate_dataset(dataset_dir)
    if not is_valid:
        print("[ERROR] Dataset validation failed before import:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("[OK] Dataset passed validation. Preparing database import...")

    berths_data = _load_csv(dataset_dir / "berths.csv")
    cranes_data = _load_csv(dataset_dir / "cranes.csv")
    yard_data = _load_csv(dataset_dir / "yard_zones.csv")
    routes_data = _load_csv(dataset_dir / "routes.csv")
    vessels_data = _load_csv(dataset_dir / "vessels.csv")
    schedules_data = _load_csv(dataset_dir / "vessel_schedule.csv")

    if dry_run:
        print(f"[DRY-RUN] Would import {len(berths_data)} berths, {len(cranes_data)} cranes, "
              f"{len(yard_data)} yard zones, {len(routes_data)} routes, {len(vessels_data)} vessels, "
              f"and {len(schedules_data)} schedules.")
        return

    async with AsyncSessionLocal() as session:
        try:
            # 1. Berths
            for b in berths_data:
                b_id = uuid.UUID(b["berth_id"])
                existing = (await session.execute(select(Berth).where(Berth.id == b_id))).scalar_one_or_none()
                if not existing:
                    session.add(
                        Berth(
                            id=b_id,
                            name=b["name"],
                            max_vessel_length_m=float(b["max_vessel_length_m"]),
                            max_draft_m=float(b["max_draft_m"]),
                            capacity=int(b["capacity"]),
                            status=BerthStatus(b["status"]),
                        )
                    )
            await session.flush()

            # 2. Cranes
            for c in cranes_data:
                c_id = uuid.UUID(c["crane_id"])
                existing = (await session.execute(select(Crane).where(Crane.id == c_id))).scalar_one_or_none()
                if not existing:
                    b_id = uuid.UUID(c["current_berth_id"]) if c.get("current_berth_id") else None
                    session.add(
                        Crane(
                            id=c_id,
                            name=c["name"],
                            status=CraneStatus(c["status"]),
                            handling_rate_containers_per_h=float(c["handling_rate_containers_per_h"]),
                            current_berth_id=b_id,
                        )
                    )

            # 3. Yard Zones
            for y in yard_data:
                y_id = uuid.UUID(y["yard_zone_id"])
                existing = (await session.execute(select(YardZone).where(YardZone.id == y_id))).scalar_one_or_none()
                if not existing:
                    session.add(
                        YardZone(
                            id=y_id,
                            name=y["name"],
                            total_capacity=int(y["total_capacity"]),
                            occupied_capacity=int(y["occupied_capacity"]),
                        )
                    )

            # 4. Routes
            for r in routes_data:
                r_id = uuid.UUID(r["route_id"])
                existing = (await session.execute(select(Route).where(Route.id == r_id))).scalar_one_or_none()
                if not existing:
                    session.add(
                        Route(
                            id=r_id,
                            name=r["name"],
                            nominal_travel_time_h=float(r["estimated_duration_h"]),
                            capacity=int(r["capacity"]),
                            route_points=json.loads(r["route_points"]),
                        )
                    )
            await session.flush()

            # 5. Vessels
            for v in vessels_data:
                v_id = uuid.UUID(v["vessel_id"])
                existing = (await session.execute(select(Vessel).where(Vessel.id == v_id))).scalar_one_or_none()
                if not existing:
                    session.add(
                        Vessel(
                            id=v_id,
                            name=v["vessel_name"],
                            imo_number=v["synthetic_vessel_id"],
                            vessel_type=VesselType(v["vessel_type"]),
                            length_m=float(v["length_m"]),
                            beam_m=float(v["beam_m"]),
                            draft_m=float(v["draft_m"]),
                            container_capacity=int(v["container_capacity"]),
                            containers_to_handle=int(v["containers_to_handle"]),
                            priority=VesselPriority(v["priority"]),
                            status=VesselStatus.at_sea,
                        )
                    )
            await session.flush()

            # 6. Schedules
            for s in schedules_data:
                s_id = uuid.UUID(s["schedule_id"])
                existing = (await session.execute(select(Schedule).where(Schedule.id == s_id))).scalar_one_or_none()
                if not existing:
                    p_start = datetime.fromisoformat(s["scheduled_arrival"])
                    p_end = datetime.fromisoformat(s["expected_departure"])
                    session.add(
                        Schedule(
                            id=s_id,
                            vessel_id=uuid.UUID(s["vessel_id"]),
                            berth_id=uuid.UUID(s["planned_berth_id"]),
                            planned_start=p_start,
                            planned_end=p_end,
                            status=ScheduleStatus.active,
                        )
                    )

            await session.commit()
            print("[SUCCESS] Dataset imported successfully into PostgreSQL!")
        except Exception as exc:
            await session.rollback()
            print(f"[ERROR] Database import failed: {exc}")
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Import synthetic dataset scenario into PostgreSQL.")
    parser.add_argument("dataset_path", type=str, help="Path to scenario directory (e.g. datasets/synthetic/demo/)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without committing to database")
    args = parser.parse_args()

    asyncio.run(import_dataset(Path(args.dataset_path), dry_run=args.dry_run))


if __name__ == "__main__":
    main()
