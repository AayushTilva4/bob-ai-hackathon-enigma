"""
Rule-based crane allocation and release manager for HarborAI.

Allocates available cranes to berthed vessels based on vessel size / workload:
- Small vessel (< 1000 containers or length < 180m): 1–2 cranes
- Medium vessel (1000–3000 containers or 180–280m): 2–3 cranes
- Large vessel (> 3000 containers or > 280m): 3–4 cranes

Guarantees:
- Cranes cannot be double-booked.
- Updates crane.current_berth_id and crane.status.
- Releases cranes when operations finish.
"""

import uuid
from typing import Sequence

from database.models import Crane, CraneStatus, Vessel


class CraneManager:
    """Deterministic, rule-based crane allocation manager."""

    @staticmethod
    def get_desired_crane_count(vessel: Vessel) -> int:
        """Determine target number of cranes based on container volume and length."""
        containers = vessel.containers_to_handle or 500
        length = vessel.length_m or 200.0

        if containers > 3000 or length > 280.0:
            return 3  # Large vessel
        elif containers >= 1000 or length >= 180.0:
            return 2  # Medium vessel
        else:
            return 1  # Small vessel

    @classmethod
    def allocate_cranes_for_vessel(
        cls,
        vessel: Vessel,
        berth_id: uuid.UUID,
        all_cranes: Sequence[Crane],
    ) -> list[Crane]:
        """
        Allocate available cranes to the specified berth.
        Cranes are sorted deterministically by name.
        """
        desired_count = cls.get_desired_crane_count(vessel)

        # Filter available cranes: status == available and current_berth_id is None
        available_cranes = [
            c
            for c in sorted(all_cranes, key=lambda c: c.name)
            if c.status == CraneStatus.available and c.current_berth_id is None
        ]

        # Allocate up to desired count, at least 1 if available
        allocated = available_cranes[:desired_count]
        for crane in allocated:
            crane.current_berth_id = berth_id
            crane.status = CraneStatus.operating

        return allocated

    @staticmethod
    def release_cranes_for_berth(
        berth_id: uuid.UUID, all_cranes: Sequence[Crane]
    ) -> list[Crane]:
        """Release all cranes currently assigned to the given berth."""
        released: list[Crane] = []
        for crane in all_cranes:
            if crane.current_berth_id == berth_id:
                crane.current_berth_id = None
                crane.status = CraneStatus.available
                released.append(crane)
        return released
