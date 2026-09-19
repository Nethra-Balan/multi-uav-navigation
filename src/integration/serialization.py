from dataclasses import asdict, is_dataclass
from typing import Any

import numpy as np

from src.chromosome import Chromosome
from src.environment import Environment


def to_json_safe(value: Any) -> Any:
    """Convert engine values into JSON-compatible Python values."""
    if isinstance(value, np.ndarray):
        return [to_json_safe(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return to_json_safe(value.item())
    if isinstance(value, Chromosome):
        return serialize_chromosome(value)
    if isinstance(value, Environment):
        return serialize_environment(value)
    if is_dataclass(value):
        return to_json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Unsupported value for JSON serialization: {type(value)!r}")


def serialize_chromosome(chromosome: Chromosome) -> dict:
    return {
        "routes": [
            [int(target_id) for target_id in route]
            for route in chromosome.routes
        ]
    }


def serialize_environment(environment: Environment) -> dict:
    return {
        "dimensions": {
            "width": float(environment.width),
            "depth": float(environment.depth),
            "height": float(environment.height),
        },
        "start_position": to_json_safe(environment.start_position),
        "uav_positions": to_json_safe(environment.uav_positions),
        "uavs": [
            {
                "id": index + 1,
                "start_position": to_json_safe(position),
            }
            for index, position in enumerate(environment.uav_positions)
        ],
        "target_positions": to_json_safe(environment.target_positions),
        "targets": [
            {
                "id": index + 1,
                "position": to_json_safe(position),
            }
            for index, position in enumerate(environment.target_positions)
        ],
        "obstacles": [
            {
                "id": index + 1,
                "min": to_json_safe(obstacle["min"]),
                "max": to_json_safe(obstacle["max"]),
            }
            for index, obstacle in enumerate(environment.obstacles)
        ],
    }


def serialize_fitness_metrics(metrics: dict) -> dict:
    return to_json_safe(metrics)


def serialize_validation(validation: dict) -> dict:
    return to_json_safe(validation)


def serialize_generation_event(event) -> dict:
    return to_json_safe(event)
