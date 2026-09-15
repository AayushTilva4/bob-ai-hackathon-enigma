"""
Unit tests for the SimulationClock.
"""

from datetime import datetime, timezone

from simulation.clock import DEFAULT_START_TIME, SimulationClock


def test_clock_initialization():
    clock = SimulationClock()
    assert clock.current_time == DEFAULT_START_TIME
    assert clock.is_running is False
    assert clock.total_steps == 0
    assert clock.elapsed_hours == 0.0


def test_clock_advance():
    clock = SimulationClock()
    t1 = clock.advance(1.0)
    assert clock.total_steps == 1
    assert clock.elapsed_hours == 1.0
    assert (t1 - DEFAULT_START_TIME).total_seconds() == 3600

    t2 = clock.advance(6.0)
    assert clock.total_steps == 2
    assert clock.elapsed_hours == 7.0
    assert (t2 - DEFAULT_START_TIME).total_seconds() == 7 * 3600


def test_clock_start_pause():
    clock = SimulationClock()
    assert clock.is_running is False
    clock.start()
    assert clock.is_running is True
    clock.pause()
    assert clock.is_running is False


def test_clock_reset():
    clock = SimulationClock()
    clock.start()
    clock.advance(10.0)
    assert clock.total_steps == 1
    assert clock.elapsed_hours == 10.0

    clock.reset()
    assert clock.current_time == DEFAULT_START_TIME
    assert clock.is_running is False
    assert clock.total_steps == 0
    assert clock.elapsed_hours == 0.0


def test_clock_custom_start_time():
    custom = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    clock = SimulationClock(start_time=custom)
    assert clock.current_time == custom
    clock.advance(2.5)
    assert (clock.current_time - custom).total_seconds() == 2.5 * 3600
