from src.path_planning import (
    calculate_total_distance,
    calculate_collision_penalty,
    calculate_task_balance
)


COLLISION_WEIGHT = 1.0
BALANCE_WEIGHT = 50.0


def calculate_fitness(
    chromosome,
    start_positions,
    target_positions,
    obstacles
):
    total_distance, route_distances = calculate_total_distance(
        chromosome,
        start_positions,
        target_positions
    )

    collision_count, collision_penalty = calculate_collision_penalty(
        chromosome,
        start_positions,
        target_positions,
        obstacles
    )

    task_balance = calculate_task_balance(route_distances)

    weighted_collision_penalty = (
        COLLISION_WEIGHT * collision_penalty
    )

    weighted_balance_penalty = (
        BALANCE_WEIGHT * task_balance
    )

    fitness = (
        total_distance
        + weighted_collision_penalty
        + weighted_balance_penalty
    )

    return {
        "fitness": fitness,
        "total_distance": total_distance,
        "collision_count": collision_count,
        "collision_penalty": weighted_collision_penalty,
        "task_balance": task_balance,
        "balance_penalty": weighted_balance_penalty,
        "route_distances": route_distances
    }