"""
Synthetic dataset validator for HarborAI.

Usage:
  python -m scripts.validate_dataset datasets/synthetic/demo/
  python -m scripts.validate_dataset datasets/synthetic/normal/
  python -m scripts.validate_dataset datasets/synthetic/congestion_stress/
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED_FILES = [
    "ports.csv",
    "berths.csv",
    "cranes.csv",
    "yard_zones.csv",
    "routes.csv",
    "vessels.csv",
    "vessel_schedule.csv",
    "containers.csv",
    "weather.csv",
    "tides.csv",
    "operational_history.csv",
    "congestion_history.csv",
    "dataset_metadata.json",
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def validate_dataset(dataset_dir: Path) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    stats: dict = {}

    # 1. Required Files Check
    for req in REQUIRED_FILES:
        fp = dataset_dir / req
        if not fp.exists():
            errors.append(f"Missing required file: {req}")

    if errors:
        return False, errors, stats

    # 2. Metadata Check
    with open(dataset_dir / "dataset_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
        if not meta.get("synthetic"):
            errors.append("dataset_metadata.json must have 'synthetic': true")
        stats["scenario"] = meta.get("scenario")
        stats["seed"] = meta.get("seed")

    # 3. Load tables
    ports = load_csv(dataset_dir / "ports.csv")
    berths = load_csv(dataset_dir / "berths.csv")
    cranes = load_csv(dataset_dir / "cranes.csv")
    yard = load_csv(dataset_dir / "yard_zones.csv")
    vessels = load_csv(dataset_dir / "vessels.csv")
    schedules = load_csv(dataset_dir / "vessel_schedule.csv")
    containers = load_csv(dataset_dir / "containers.csv")
    weather = load_csv(dataset_dir / "weather.csv")
    tides = load_csv(dataset_dir / "tides.csv")
    ops = load_csv(dataset_dir / "operational_history.csv")
    congestion = load_csv(dataset_dir / "congestion_history.csv")

    stats["vessels_count"] = len(vessels)
    stats["containers_count"] = len(containers)
    stats["schedules_count"] = len(schedules)
    stats["operational_rows"] = len(ops)

    # 4. Quantity minimum checks
    if len(vessels) < 50:
        errors.append(f"Expected at least 50 vessels, found {len(vessels)}")
    if len(containers) < 5000:
        errors.append(f"Expected at least 5,000 containers, found {len(containers)}")
    if len(ops) < 2160:  # 90 days * 24 hours
        errors.append(f"Expected at least 2,160 hourly operational records, found {len(ops)}")

    # 5. ID Uniqueness
    vessel_ids = set()
    for v in vessels:
        vid = v["vessel_id"]
        if vid in vessel_ids:
            errors.append(f"Duplicate vessel_id: {vid}")
        vessel_ids.add(vid)

    container_ids = set()
    for c in containers:
        cid = c["container_id"]
        if cid in container_ids:
            errors.append(f"Duplicate container_id: {cid}")
        container_ids.add(cid)

    berth_ids = {b["berth_id"] for b in berths}
    yard_ids = {y["yard_zone_id"] for y in yard}

    # 6. Referential Integrity
    for c in containers:
        if c["vessel_id"] not in vessel_ids:
            errors.append(f"Orphan container: vessel_id {c['vessel_id']} not found")
            break
        if c["destination_zone_id"] not in yard_ids:
            errors.append(f"Invalid yard zone on container: {c['destination_zone_id']}")
            break

    for s in schedules:
        if s["vessel_id"] not in vessel_ids:
            errors.append(f"Orphan schedule: vessel_id {s['vessel_id']} not found")
            break
        if s["planned_berth_id"] not in berth_ids:
            errors.append(f"Invalid planned berth on schedule: {s['planned_berth_id']}")
            break

    # 7. Non-negative bounds & range checks
    for y in yard:
        occ = int(y["occupied_capacity"])
        cap = int(y["total_capacity"])
        if occ < 0:
            errors.append(f"Negative yard occupancy in zone {y['zone_code']}")
        if occ > cap:
            errors.append(f"Yard occupancy exceeds capacity in zone {y['zone_code']}")

    for row in ops:
        b_util = float(row["berth_utilization"])
        c_util = float(row["crane_utilization"])
        y_util = float(row["yard_utilization"])
        if not (0.0 <= b_util <= 1.0):
            errors.append(f"Berth utilization out of bounds [0, 1]: {b_util}")
            break
        if not (0.0 <= c_util <= 1.0):
            errors.append(f"Crane utilization out of bounds [0, 1]: {c_util}")
            break
        if not (0.0 <= y_util <= 1.0):
            errors.append(f"Yard utilization out of bounds [0, 1]: {y_util}")
            break
        if int(row["queue_length"]) < 0:
            errors.append("Negative queue length detected")
            break

    # 8. Congestion Target Labels & Class Balance Check
    labels = [c["future_congestion_risk_6h"] for c in congestion]
    valid_labels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    invalid = set(labels) - valid_labels
    if invalid:
        errors.append(f"Invalid congestion risk labels found: {invalid}")

    class_counts = Counter(labels)
    stats["class_distribution"] = dict(class_counts)

    # Ensure multiple classes exist (not trivial 100% single class)
    if len(class_counts) < 2:
        errors.append(f"Poor class diversity: only {len(class_counts)} class represented: {class_counts}")

    # 9. Data Leakage Verification
    # Assert that operational_history columns do NOT contain future labels or targets
    forbidden_leakage_cols = {
        "future_congestion_risk_6h",
        "future_congestion_index_6h",
        "target",
        "actual_future_waiting_time",
    }
    ops_cols = set(ops[0].keys())
    leaked = ops_cols.intersection(forbidden_leakage_cols)
    if leaked:
        errors.append(f"Data leakage detected! Forbidden columns in operational_history: {leaked}")

    is_valid = len(errors) == 0
    return is_valid, errors, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate synthetic dataset integrity.")
    parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to dataset directory (e.g. datasets/synthetic/demo/)",
    )
    args = parser.parse_args()

    d_path = Path(args.dataset_path)
    if not d_path.exists():
        print(f"[ERROR] Path does not exist: {d_path}")
        sys.exit(1)

    print("==================================================")
    print(f"HARBORAI DATASET VALIDATOR")
    print(f"Validating: {d_path.resolve()}")
    print("==================================================")

    is_valid, errors, stats = validate_dataset(d_path)

    if is_valid:
        print("\n[VALIDATION PASSED] All checks passed successfully!")
        print(f"  Scenario:             {stats.get('scenario')}")
        print(f"  Seed:                 {stats.get('seed')}")
        print(f"  Vessels:              {stats.get('vessels_count')}")
        print(f"  Containers:           {stats.get('containers_count')}")
        print(f"  Schedules:            {stats.get('schedules_count')}")
        print(f"  Operational rows:     {stats.get('operational_rows')}")
        print(f"  Class distribution:   {stats.get('class_distribution')}")
        print("==================================================")
        sys.exit(0)
    else:
        print(f"\n[VALIDATION FAILED] Found {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        print("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
