import numpy as np

from src.waypoints import build_collision_aware_path
from src.collision import segment_intersects_obstacle


COLLISION_PENALTY = 5000.0
BALANCE_WEIGHT = 10.0


def calculate_path_distance(path):
    total_distance = 0.0

    for i in range(len(path) - 1):
        total_distance += np.linalg.norm(
            path[i + 1] - path[i]
        )

    return total_distance


def path_has_collision(path, obstacles):
    for i in range(len(path) - 1):

        start = path[i]
        end = path[i + 1]

        for obstacle in obstacles:

            if segment_intersects_obstacle(
                start,
                end,
                obstacle
            ):
                return True

    return False


def calculate_fitness(
    chromosome,
    uav_positions,
    target_positions,
    obstacles
):
    route_distances = []
    collision_count = 0

    for uav_index, route in enumerate(
        chromosome.routes
    ):

        path = build_collision_aware_path(
            uav_positions[uav_index],
            route,
            target_positions,
            obstacles
        )

        distance = calculate_path_distance(path)

        route_distances.append(distance)

        if path_has_collision(
            path,
            obstacles
        ):
            collision_count += 1

    total_distance = sum(route_distances)

    balance_penalty = np.std(
        route_distances
    )

    collision_penalty = (
        collision_count * COLLISION_PENALTY
    )

    fitness = (
        total_distance
        + collision_penalty
        + BALANCE_WEIGHT * balance_penalty
    )

    return {
        "fitness": fitness,
        "total_distance": total_distance,
        "collision_count": collision_count,
        "collision_penalty": collision_penalty,
        "balance_penalty": balance_penalty,
        "route_distances": route_distances
    }