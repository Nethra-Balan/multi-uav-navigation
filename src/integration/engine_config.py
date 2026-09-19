from dataclasses import dataclass
from typing import Tuple

from src.adaptive_mutation import (
    MAX_MUTATION_PROBABILITY,
    MIN_MUTATION_PROBABILITY,
)
from src.crossover import CROSSOVER_PROBABILITY
from src.fitness import BALANCE_WEIGHT, COLLISION_PENALTY
from src.mutation import MUTATION_PROBABILITY


@dataclass(frozen=True)
class EngineConfig:
    """Validated configuration shared by the engine integrations."""

    environment_size: Tuple[float, float, float] = (200.0, 200.0, 100.0)
    seed: int = 42
    num_uavs: int = 6
    num_targets: int = 30
    num_obstacles: int = 8
    population_size: int = 10
    generations: int = 30
    elite_count: int = 2
    crossover_probability: float = CROSSOVER_PROBABILITY
    fixed_mutation_probability: float = MUTATION_PROBABILITY
    adaptive_mutation_minimum: float = MIN_MUTATION_PROBABILITY
    adaptive_mutation_maximum: float = MAX_MUTATION_PROBABILITY
    collision_penalty: float = COLLISION_PENALTY
    balance_weight: float = BALANCE_WEIGHT

    def __post_init__(self):
        if len(self.environment_size) != 3:
            raise ValueError("environment_size must contain three dimensions")
        if any(dimension <= 0 for dimension in self.environment_size):
            raise ValueError("environment dimensions must be positive")
        if self.num_uavs <= 0 or self.num_targets < self.num_uavs:
            raise ValueError("num_targets must be at least num_uavs")
        if self.num_obstacles < 0 or self.population_size <= 0:
            raise ValueError("counts must be non-negative and population_size positive")
        if self.generations <= 0 or self.elite_count < 0:
            raise ValueError("generations must be positive and elite_count non-negative")
        if self.elite_count > self.population_size:
            raise ValueError("elite_count cannot exceed population_size")
        for probability in (
            self.crossover_probability,
            self.fixed_mutation_probability,
            self.adaptive_mutation_minimum,
            self.adaptive_mutation_maximum,
        ):
            if not 0.0 <= probability <= 1.0:
                raise ValueError("probabilities must be between 0 and 1")
        if self.adaptive_mutation_minimum > self.adaptive_mutation_maximum:
            raise ValueError("adaptive mutation minimum cannot exceed maximum")
        if self.collision_penalty < 0.0 or self.balance_weight < 0.0:
            raise ValueError("penalty and balance weight must be non-negative")
