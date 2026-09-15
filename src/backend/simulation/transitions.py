"""
Vessel lifecycle state transition validator for HarborAI.

Implements the strict operational vessel lifecycle:
AT_SEA -> APPROACHING_PORT (approaching) -> WAITING or BERTH_ASSIGNED
WAITING -> BERTH_ASSIGNED
BERTH_ASSIGNED -> ENTERING_BERTH
ENTERING_BERTH -> AT_BERTH
AT_BERTH -> CRANE_OPERATIONS
CRANE_OPERATIONS -> DEPARTING
DEPARTING -> LEFT_PORT

Rejects invalid, backwards, or skipped transitions.
"""

from database.models import VesselStatus


class InvalidStateTransitionError(ValueError):
    """Raised when an invalid state transition is attempted."""

    def __init__(
        self, current_status: VesselStatus, target_status: VesselStatus, reason: str = ""
    ) -> None:
        msg = f"Invalid vessel transition: cannot transition from '{current_status.value}' to '{target_status.value}'"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)
        self.current_status = current_status
        self.target_status = target_status


# Set of permitted transitions from each state
VALID_TRANSITIONS: dict[VesselStatus, set[VesselStatus]] = {
    VesselStatus.at_sea: {VesselStatus.approaching},
    VesselStatus.approaching: {VesselStatus.waiting, VesselStatus.berth_assigned},
    VesselStatus.waiting: {VesselStatus.berth_assigned},
    VesselStatus.berth_assigned: {VesselStatus.entering_berth},
    VesselStatus.entering_berth: {VesselStatus.at_berth},
    VesselStatus.at_berth: {VesselStatus.crane_operations},
    VesselStatus.crane_operations: {VesselStatus.departing},
    VesselStatus.departing: {VesselStatus.left_port},
    VesselStatus.left_port: set(),  # Terminal state
}


def can_transition(current: VesselStatus, target: VesselStatus) -> bool:
    """Return True if transitioning from current to target is allowed."""
    return target in VALID_TRANSITIONS.get(current, set())


def validate_transition(
    current: VesselStatus, target: VesselStatus, reason: str = ""
) -> None:
    """Validate transition and raise InvalidStateTransitionError if illegal."""
    if not can_transition(current, target):
        raise InvalidStateTransitionError(current, target, reason)
