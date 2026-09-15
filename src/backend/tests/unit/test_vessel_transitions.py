"""
Unit tests for vessel lifecycle state transitions.
"""

import pytest

from database.models import VesselStatus
from simulation.transitions import (
    InvalidStateTransitionError,
    can_transition,
    validate_transition,
)


def test_valid_lifecycle_transitions():
    # AT_SEA -> APPROACHING
    assert can_transition(VesselStatus.at_sea, VesselStatus.approaching)

    # APPROACHING -> WAITING or BERTH_ASSIGNED
    assert can_transition(VesselStatus.approaching, VesselStatus.waiting)
    assert can_transition(VesselStatus.approaching, VesselStatus.berth_assigned)

    # WAITING -> BERTH_ASSIGNED
    assert can_transition(VesselStatus.waiting, VesselStatus.berth_assigned)

    # BERTH_ASSIGNED -> ENTERING_BERTH
    assert can_transition(VesselStatus.berth_assigned, VesselStatus.entering_berth)

    # ENTERING_BERTH -> AT_BERTH
    assert can_transition(VesselStatus.entering_berth, VesselStatus.at_berth)

    # AT_BERTH -> CRANE_OPERATIONS
    assert can_transition(VesselStatus.at_berth, VesselStatus.crane_operations)

    # CRANE_OPERATIONS -> DEPARTING
    assert can_transition(VesselStatus.crane_operations, VesselStatus.departing)

    # DEPARTING -> LEFT_PORT
    assert can_transition(VesselStatus.departing, VesselStatus.left_port)


def test_invalid_transitions_rejected():
    # Terminal state cannot transition anywhere
    assert not can_transition(VesselStatus.left_port, VesselStatus.at_sea)
    assert not can_transition(VesselStatus.left_port, VesselStatus.approaching)

    # Cannot skip straight from at_sea to at_berth
    assert not can_transition(VesselStatus.at_sea, VesselStatus.at_berth)

    # Cannot skip from waiting to departing
    assert not can_transition(VesselStatus.waiting, VesselStatus.departing)

    # Cannot move backwards from crane_operations to approaching
    assert not can_transition(VesselStatus.crane_operations, VesselStatus.approaching)


def test_validate_transition_raises_exception():
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        validate_transition(VesselStatus.left_port, VesselStatus.at_sea)
    assert "Invalid vessel transition" in str(exc_info.value)
