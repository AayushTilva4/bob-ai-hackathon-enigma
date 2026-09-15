"""
Yard operations and capacity management for HarborAI.

Handles container placement, discharge, dwell departures, and capacity constraints:
- Never allows occupied_capacity < 0.
- Never allows occupied_capacity > total_capacity.
- Calculates computed utilization safely.
- Selects target YardZone deterministically based on available capacity and lowest utilization.
"""

from typing import Sequence

from database.models import YardZone


class YardManager:
    """Deterministic yard zone manager."""

    @staticmethod
    def select_best_zone(
        zones: Sequence[YardZone], containers_to_store: int
    ) -> YardZone | None:
        """
        Find the best yard zone able to accommodate containers_to_store.
        Picks the zone with sufficient free capacity, sorted by lowest utilization
        and deterministically by name.
        """
        feasible = [
            z
            for z in zones
            if (z.total_capacity - z.occupied_capacity) >= containers_to_store
        ]
        if not feasible:
            # Fallback: zone with maximum remaining capacity
            return max(
                zones,
                key=lambda z: (z.total_capacity - z.occupied_capacity, -ord(z.name[0])),
                default=None,
            )

        # Sort by lowest utilization, then by name
        return min(feasible, key=lambda z: (z.utilization, z.name))

    @staticmethod
    def discharge_containers(zone: YardZone, count: int) -> int:
        """
        Add unloaded containers to the yard zone up to total_capacity.
        Returns the number of containers actually stored.
        """
        if count <= 0:
            return 0
        available_space = max(0, zone.total_capacity - zone.occupied_capacity)
        to_add = min(count, available_space)
        zone.occupied_capacity += to_add
        return to_add

    @staticmethod
    def release_containers(zone: YardZone, count: int) -> int:
        """
        Remove containers from the yard zone (e.g. gates/rail departure).
        Ensures occupancy never drops below 0.
        Returns the number of containers actually removed.
        """
        if count <= 0:
            return 0
        to_remove = min(count, zone.occupied_capacity)
        zone.occupied_capacity -= to_remove
        return to_remove
