"""
CLI entrypoint to generate synthetic datasets for HarborAI.

Usage:
  python -m scripts.generate_dataset --scenario normal --days 90 --seed 42
  python -m scripts.generate_dataset --scenario congestion_stress --days 90 --seed 42
  python -m scripts.generate_dataset --scenario demo --days 90 --seed 42
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from generator.pipeline import DatasetGenerationPipeline
from generator.scenario_config import get_scenario_config


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reproducible synthetic port operations datasets for HarborAI."
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="normal",
        choices=["normal", "congestion_stress", "demo"],
        help="Scenario type to generate (default: normal)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of historical days to simulate (default: 90)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic reproducibility (default: 42)",
    )
    parser.add_argument(
        "--vessels",
        type=int,
        default=None,
        help="Override number of synthetic vessels (default: scenario standard >= 50)",
    )
    parser.add_argument(
        "--containers",
        type=int,
        default=None,
        help="Override number of synthetic containers (default: scenario standard >= 5000)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Destination directory (default: datasets/synthetic/<scenario>)",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = repo_root / "datasets" / "synthetic" / args.scenario

    overrides = {}
    if args.vessels is not None:
        overrides["num_vessels"] = args.vessels
    if args.containers is not None:
        overrides["num_containers"] = args.containers

    config = get_scenario_config(
        name=args.scenario, seed=args.seed, days=args.days, **overrides
    )

    print("==================================================")
    print(f"HARBORAI SYNTHETIC DATASET GENERATOR")
    print(f"Scenario:     {config.name.upper()}")
    print(f"Seed:         {config.seed}")
    print(f"Days:         {config.days} ({config.days * 24} hours)")
    print(f"Output Dir:   {out_dir}")
    print("==================================================")

    pipeline = DatasetGenerationPipeline(config)
    result = pipeline.run(out_dir)

    print(f"\n[OK] Dataset generated successfully!")
    print(f"  Vessels:             {result['vessels']}")
    print(f"  Containers:          {result['containers']}")
    print(f"  Schedules:           {result['schedules']}")
    print(f"  Operational rows:    {result['operational_rows']}")
    print(f"  Weather rows:        {result['weather_rows']}")
    print(f"  Tide rows:           {result['tide_rows']}")
    print(f"  Congestion rows:     {result['congestion_rows']}")
    print(f"  Metadata:            {out_dir / 'dataset_metadata.json'}")


if __name__ == "__main__":
    main()
