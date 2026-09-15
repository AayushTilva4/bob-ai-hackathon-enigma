"""
Rule-based berth feasibility, assignment, and release manager for HarborAI.

NO OR-Tools or mathematical optimization in Phase 2.
Implements simple, deterministic feasibility rules:
- Berth must be available (and not currently occupied by another vessel).
- Vessel length_m <= berth.max_vessel_length_m.
- Vessel draft_m <= berth.max_draft_m.
- Incompatible berths are strictly rejected.
- When vessel departs, berth is released.
- Strictly adheres to Phase 1 architecture: NO berths.current_vessel_id column.
"""

import uuid
from typing import Sequence

from database.models import Berth, BerthStatus, Vessel


class BerthManager:
    """Deterministic, rule-based berth manager."""

    @staticmethod
    def is_feasible(vessel: Vessel, berth: Berth) -> bool:
        """
        Check physical compatibility between vessel and berth:
        1. Vessel length must fit within berth max length.
        2. Vessel draft must not exceed berth max draft.
        """
        if vessel.length_m > berth.max_vessel_length_m:
            return False
        if vessel.draft_m > berth.max_draft_m:
            return False
        return True

    @classmethod
    def find_best_feasible_berth(
        cls,
        vessel: Vessel,
        berths: Sequence[Berth],
        occupied_berth_ids: set[uuid.UUID],
    ) -> Berth | None:
        """
        Find the first available and physically feasible berth.
        Sorted deterministically by berth name.
        """
        # Sort berths deterministically by name
        sorted_berths = sorted(berths, key=lambda b: b.name)

        for berth in sorted_berths:
            # Check availability: status must be available and not in active occupied set
            if berth.status != BerthStatus.available:
                continue
            if berth.id in occupied_berth_ids:
                continue

            # Check physical feasibility
            if cls.is_feasible(vessel, berth):
                return berth

        return None

    @staticmethod
    def assign_berth(vessel: Vessel, berth: Berth) -> None:
        """Assign vessel to berth and update statuses."""
        vessel.assigned_berth_id = berth.id
        berth.status = BerthStatus.occupied

    @staticmethod
    def release_berth(vessel: Vessel, berth: Berth) -> None:
        """Release berth upon vessel departure."""
        vessel.assigned_berth_id = None
        berth.status = BerthStatus.available
