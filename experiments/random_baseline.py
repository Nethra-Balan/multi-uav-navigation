import os
import sys
import csv
import random

import numpy as np


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
from src.fitness import calculate_fitness


def run_baseline():

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
        generations=20,
        elite_count=2
    )

    best_chromosome, best_fitness = (
        algorithm.run()
    )

    ga_result = calculate_fitness(
        best_chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    rng = np.random.default_rng(
        RANDOM_SEED + 100
    )

    random_routes = []

    targets = list(
        range(1, NUM_TARGETS + 1)
    )

    rng.shuffle(targets)

    split_points = np.array_split(
        targets,
        NUM_UAVS
    )

    for route in split_points:
        random_routes.append(
            route.tolist()
        )

    random_chromosome = type(
        best_chromosome
    )(
        random_routes
    )

    random_result = calculate_fitness(
        random_chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    ga_fitness = ga_result["fitness"]
    random_fitness = random_result["fitness"]

    improvement = (
        (random_fitness - ga_fitness)
        / random_fitness
    ) * 100

    output_file = os.path.join(
        PROJECT_ROOT,
        "results",
        "data",
        "baseline_comparison.csv"
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
            "Method",
            "Fitness",
            "Total Distance",
            "Collision Count",
            "Collision Penalty",
            "Balance Penalty"
        ])

        writer.writerow([
            "Random Baseline",
            random_result["fitness"],
            random_result["total_distance"],
            random_result["collision_count"],
            random_result["collision_penalty"],
            random_result["balance_penalty"]
        ])

        writer.writerow([
            "Genetic Algorithm",
            ga_result["fitness"],
            ga_result["total_distance"],
            ga_result["collision_count"],
            ga_result["collision_penalty"],
            ga_result["balance_penalty"]
        ])

    print()
    print(
        "Baseline comparison completed."
    )
    print()
    print(
        f"Random Baseline Fitness : "
        f"{random_fitness:.2f}"
    )

    print(
        f"Genetic Algorithm Fitness: "
        f"{ga_fitness:.2f}"
    )

    print(
        f"Improvement              : "
        f"{improvement:.2f}%"
    )

    print()
    print(
        "Comparison saved to: "
        "results/data/baseline_comparison.csv"
    )


if __name__ == "__main__":
    run_baseline()