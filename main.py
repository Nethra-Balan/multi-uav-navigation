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
from src.genetic_algorithm import GeneticAlgorithm


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

    genetic_algorithm = GeneticAlgorithm(
        population=population,
        environment=environment,
        generations=20,
        elite_count=2
    )

    best_chromosome, best_fitness = genetic_algorithm.run()

    print("\nOptimization completed.")

    print(
        f"Best fitness: {best_fitness:.2f}"
    )

    print(
        "Best chromosome routes:"
    )

    for i, route in enumerate(
        best_chromosome.routes
    ):

        print(
            f"UAV {i + 1}: {route}"
        )

    print(
        "\nValid best chromosome:",
        best_chromosome.is_valid(
            NUM_TARGETS,
            NUM_UAVS
        )
    )


if __name__ == "__main__":
    main()