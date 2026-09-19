from typing import Any, Dict, List

import numpy as np

from src.collision import segment_intersects_obstacle
from src.fitness import calculate_fitness
from src.path_validation import validate_chromosome
from src.waypoints import build_collision_aware_path

from src.integration.serialization import (
    serialize_chromosome,
    serialize_fitness_metrics,
    serialize_validation,
    to_json_safe,
)


def _is_target(point, target_positions) -> bool:
    return any(np.array_equal(point, target) for target in target_positions)


def extract_final_result(
    chromosome,
    environment,
    collision_penalty_weight=None,
    balance_weight=None
) -> Dict[str, Any]:
    fitness_kwargs = {}
    if collision_penalty_weight is not None and balance_weight is not None:
        fitness_kwargs = {
            "collision_penalty_weight": collision_penalty_weight,
            "balance_weight": balance_weight,
        }
    metrics = calculate_fitness(
        chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles,
        **fitness_kwargs
    )
    validation = validate_chromosome(
        chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles,
    )

    paths: List[List[Any]] = []
    waypoints: List[List[Any]] = []
    allocation = []
    collisions = []

    for uav_index, route in enumerate(chromosome.routes):
        path = build_collision_aware_path(
            environment.uav_positions[uav_index],
            route,
            environment.target_positions,
            environment.obstacles,
        )
        paths.append(to_json_safe(path))
        waypoints.append([
            to_json_safe(point)
            for point in path[1:-1]
            if not _is_target(point, environment.target_positions)
        ])
        allocation.append({
            "uav": uav_index + 1,
            "targets": [int(target_id) for target_id in route],
            "target_count": len(route),
            "path_distance": float(metrics["route_distances"][uav_index]),
        })

        for segment_index, (start, end) in enumerate(zip(path, path[1:])):
            for obstacle_index, obstacle in enumerate(environment.obstacles):
                if segment_intersects_obstacle(start, end, obstacle):
                    collisions.append({
                        "uav": uav_index + 1,
                        "segment_index": segment_index,
                        "start": to_json_safe(start),
                        "end": to_json_safe(end),
                        "obstacle": obstacle_index + 1,
                    })

    return {
        "best_chromosome": serialize_chromosome(chromosome),
        "paths": paths,
        "waypoints": waypoints,
        "allocation": allocation,
        "collisions": collisions,
        "metrics": serialize_fitness_metrics(metrics),
        "validation": serialize_validation(validation),
    }
