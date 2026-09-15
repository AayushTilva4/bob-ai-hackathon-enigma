"""
Simulation Clock for HarborAI.

Provides deterministic discrete time progression decoupled from wall-clock time.
Supports start, pause, reset, and advance by configurable hourly increments.
"""

from datetime import datetime, timedelta, timezone

DEFAULT_START_TIME = datetime(2026, 1, 15, 6, 0, 0, tzinfo=timezone.utc)


class SimulationClock:
    """Deterministic simulation clock."""

    def __init__(
        self,
        start_time: datetime | None = None,
        default_step_hours: float = 1.0,
    ) -> None:
        self._initial_time = (
            start_time if start_time is not None else DEFAULT_START_TIME
        )
        if self._initial_time.tzinfo is None:
            self._initial_time = self._initial_time.replace(tzinfo=timezone.utc)
        self._current_time = self._initial_time
        self._default_step_hours = default_step_hours
        self._is_running = False
        self._total_steps = 0
        self._elapsed_hours = 0.0

    @property
    def current_time(self) -> datetime:
        return self._current_time

    @property
    def initial_time(self) -> datetime:
        return self._initial_time

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def default_step_hours(self) -> float:
        return self._default_step_hours

    @property
    def total_steps(self) -> int:
        return self._total_steps

    @property
    def elapsed_hours(self) -> float:
        return self._elapsed_hours

    def start(self) -> None:
        """Start or resume progression."""
        self._is_running = True

    def pause(self) -> None:
        """Pause progression."""
        self._is_running = False

    def reset(self, start_time: datetime | None = None) -> None:
        """Reset the clock back to initial timestamp."""
        if start_time is not None:
            self._initial_time = (
                start_time
                if start_time.tzinfo is not None
                else start_time.replace(tzinfo=timezone.utc)
            )
        self._current_time = self._initial_time
        self._is_running = False
        self._total_steps = 0
        self._elapsed_hours = 0.0

    def advance(self, hours: float | None = None) -> datetime:
        """Advance simulation time by the specified number of hours."""
        increment = (
            hours if hours is not None and hours > 0 else self._default_step_hours
        )
        self._current_time += timedelta(hours=increment)
        self._total_steps += 1
        self._elapsed_hours += increment
        return self._current_time
