from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator

from src.integration.engine_config import EngineConfig


class AlgorithmMode(str, Enum):
    fixed = "fixed"
    adaptive = "adaptive"


class MissionConfigRequest(BaseModel):
    environment_dimensions: Tuple[float, float, float] = (200.0, 200.0, 100.0)
    seed: int = 42
    uav_count: int = Field(6, ge=1)
    target_count: int = Field(30, ge=1)
    obstacle_count: int = Field(8, ge=0)
    population_size: int = Field(10, ge=1)
    generations: int = Field(30, ge=1)
    elite_count: int = Field(2, ge=0)
    crossover_probability: float = Field(0.85, ge=0.0, le=1.0)
    fixed_mutation_probability: float = Field(0.15, ge=0.0, le=1.0)
    adaptive_mutation_minimum: float = Field(0.05, ge=0.0, le=1.0)
    adaptive_mutation_maximum: float = Field(0.30, ge=0.0, le=1.0)
    collision_penalty: float = Field(5000.0, ge=0.0)
    balance_weight: float = Field(10.0, ge=0.0)
    algorithm: AlgorithmMode = AlgorithmMode.adaptive

    @field_validator("environment_dimensions")
    @classmethod
    def validate_dimensions(cls, value):
        if len(value) != 3 or any(dimension <= 0 for dimension in value):
            raise ValueError("environment_dimensions must contain three positive values")
        return value

    def to_engine_config(self) -> EngineConfig:
        return EngineConfig(
            environment_size=self.environment_dimensions,
            seed=self.seed,
            num_uavs=self.uav_count,
            num_targets=self.target_count,
            num_obstacles=self.obstacle_count,
            population_size=self.population_size,
            generations=self.generations,
            elite_count=self.elite_count,
            crossover_probability=self.crossover_probability,
            fixed_mutation_probability=self.fixed_mutation_probability,
            adaptive_mutation_minimum=self.adaptive_mutation_minimum,
            adaptive_mutation_maximum=self.adaptive_mutation_maximum,
            collision_penalty=self.collision_penalty,
            balance_weight=self.balance_weight,
        )


class MissionResponse(BaseModel):
    mission_id: str
    status: str
    configuration: Dict[str, Any]
    environment: Dict[str, Any]


class LifecycleResponse(BaseModel):
    mission_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    engine_available: bool


class WebSocketMessage(BaseModel):
    type: str
    mission_id: str
    payload: Dict[str, Any]


class StatusResponse(BaseModel):
    mission_id: str
    status: str
    generation: Optional[int] = None
    total_generations: int
    best_fitness: Optional[float] = None
    mean_fitness: Optional[float] = None
    mutation_probability: Optional[float] = None
    total_path_distance: Optional[float] = None
    collision_count: Optional[int] = None
    balance_penalty: Optional[float] = None
    route_distances: Optional[List[float]] = None
    target_counts: Optional[List[int]] = None
