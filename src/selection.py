import random

from src.fitness import calculate_fitness


TOURNAMENT_SIZE = 3


def tournament_selection(
    population,
    num_selected,
    start_positions,
    target_positions,
    obstacles,
    collision_penalty_weight=None,
    balance_weight=None
):
    selected = []

    for _ in range(num_selected):
        tournament = random.sample(
            population,
            TOURNAMENT_SIZE
        )

        best_chromosome = min(
            tournament,
            key=lambda chromosome: calculate_fitness(
                chromosome,
                start_positions,
                target_positions,
                obstacles,
                **({
                    "collision_penalty_weight": collision_penalty_weight,
                    "balance_weight": balance_weight
                } if collision_penalty_weight is not None and balance_weight is not None else {})
            )["fitness"]
        )

        selected.append(best_chromosome)

    return selected