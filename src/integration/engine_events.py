from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from src.chromosome import Chromosome


@dataclass(frozen=True)
class GenerationEvent:
    generation: int
    total_generations: int
    best_fitness: float
    mean_fitness: Optional[float]
    mutation_probability: Optional[float]
    total_path_distance: float
    collision_count: int
    balance_penalty: float
    route_distances: List[float]
    target_counts: List[int]
    best_chromosome: Chromosome
    best_routes: List[List[int]]
    best_fitness_result: Dict[str, Any]


GenerationCallback = Callable[[GenerationEvent], None]
