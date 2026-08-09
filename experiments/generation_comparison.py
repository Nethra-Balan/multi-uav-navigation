import os
import sys
import csv
import random


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)

from config import (
    ENVIRONMENT_SIZE,
    NUM_UAVS,
    NUM_TARGETS,
    NUM_OBSTACLES,
    RANDOM_SEED
)

from src.environment import Environment
from src.population import generate_population
from src.genetic_algorithm import GeneticAlgorithm


GENERATION_VALUES = [
    10,
    20,
    30,
    40,
    50
]


results = []


for generations in GENERATION_VALUES:

    random.seed(RANDOM_SEED)

    environment = Environment(
        size=ENVIRONMENT_SIZE,
        num_uavs=NUM_UAVS,
        num_targets=NUM_TARGETS,
        num_obstacles=NUM_OBSTACLES,
        random_seed=RANDOM_SEED
    )

    population = generate_population(
        num_individuals=10,
        num_targets=NUM_TARGETS,
        num_uavs=NUM_UAVS,
        random_seed=RANDOM_SEED
    )

    algorithm = GeneticAlgorithm(
        population=population,
        environment=environment,
        generations=generations,
        elite_count=2
    )

    best_chromosome, best_fitness = (
        algorithm.run()
    )

    results.append(
        {
            "generations": generations,
            "best_fitness": best_fitness
        }
    )

    print(
        f"Generations: {generations} | "
        f"Best Fitness: {best_fitness:.2f}"
    )


output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "data",
    "generation_comparison.csv"
)


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


with open(
    output_file,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Generations",
        "Best Fitness"
    ])

    for result in results:

        writer.writerow([
            result["generations"],
            result["best_fitness"]
        ])


print()
print(
    "Generation comparison completed."
)

print(
    "Results saved to: "
    "results/data/generation_comparison.csv"
)