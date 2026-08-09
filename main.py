from config import (
    ENVIRONMENT_SIZE,
    NUM_UAVS,
    NUM_TARGETS,
    NUM_OBSTACLES,
    RANDOM_SEED
)

from src.environment import Environment
from src.visualization import plot_environment
from src.population import generate_population
from src.fitness import calculate_fitness
from src.selection import tournament_selection
from src.crossover import crossover_population


def main():
    environment = Environment(
        size=ENVIRONMENT_SIZE,
        num_uavs=NUM_UAVS,
        num_targets=NUM_TARGETS,
        num_obstacles=NUM_OBSTACLES,
        random_seed=RANDOM_SEED
    )

    plot_environment(environment)

    population = generate_population(
        num_individuals=10,
        num_targets=NUM_TARGETS,
        num_uavs=NUM_UAVS
    )

    selected = tournament_selection(
        population,
        num_selected=len(population),
        start_positions=environment.uav_positions,
        target_positions=environment.target_positions,
        obstacles=environment.obstacles
    )

    children = crossover_population(selected)

    print("Crossover results:")

    for i, chromosome in enumerate(children):
        result = calculate_fitness(
            chromosome,
            environment.uav_positions,
            environment.target_positions,
            environment.obstacles
        )

        print(
            f"Child {i + 1}: "
            f"Fitness = {result['fitness']:.2f}"
        )

        print(
            f"Routes: {chromosome.routes}"
        )

        print(
            f"Valid chromosome: "
            f"{chromosome.is_valid(NUM_TARGETS, NUM_UAVS)}"
        )


if __name__ == "__main__":
    main()