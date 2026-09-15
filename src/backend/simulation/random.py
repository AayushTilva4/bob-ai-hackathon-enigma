"""
Centralized deterministic pseudo-random generator for HarborAI simulation.

Every simulation run supports a deterministic random seed (default 42).
No uncontrolled or scattered random calls are permitted across the codebase.
"""

import random


class SimulationRandom:
    """Centralized random generator ensuring reproducible simulation runs."""

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def set_seed(self, seed: int) -> None:
        """Reset the random generator with a specific seed."""
        self._seed = seed
        self._rng.seed(seed)

    @property
    def seed(self) -> int:
        return self._seed

    def uniform(self, a: float, b: float) -> float:
        """Return a random floating point number N such that a <= N <= b."""
        return self._rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        """Return a random integer N such that a <= N <= b."""
        return self._rng.randint(a, b)

    def choice(self, seq):
        """Return a random element from the non-empty sequence seq."""
        return self._rng.choice(seq)

    def sample(self, population, k: int):
        """Return a k length list of unique elements chosen from the population."""
        return self._rng.sample(population, k)
