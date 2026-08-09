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
from src.mutation import mutate_population
from src.elitism import select_elites


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

    fitness_values = []

    for chromosome in population:
        result = calculate_fitness(
            chromosome,
            environment.uav_positions,
            environment.target_positions,
            environment.obstacles
        )

        fitness_values.append(result["fitness"])

    print("Initial population fitness:")

    for i, fitness in enumerate(fitness_values):
        print(f"Chromosome {i + 1}: {fitness:.2f}")

    elites = select_elites(
        population,
        fitness_values,
        elite_count=2
    )

    print("\nElite chromosomes:")

    for i, chromosome in enumerate(elites):
        elite_fitness = calculate_fitness(
            chromosome,
            environment.uav_positions,
            environment.target_positions,
            environment.obstacles
        )["fitness"]

        print(f"Elite {i + 1}: Fitness = {elite_fitness:.2f}")
        print(f"Routes: {chromosome.routes}")
        print(
            "Valid chromosome:",
            chromosome.is_valid(NUM_TARGETS, NUM_UAVS)
        )


if __name__ == "__main__":
    main()