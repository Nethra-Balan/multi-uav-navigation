import os
import sys
import csv
import pickle

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
from src.fitness import calculate_fitness


def create_random_chromosome(
    num_targets,
    num_uavs,
    rng
):
    targets = list(
        range(1, num_targets + 1)
    )

    rng.shuffle(targets)

    routes = [
        []
        for _ in range(num_uavs)
    ]

    for index, target in enumerate(targets):
        routes[
            index % num_uavs
        ].append(target)

    return routes


environment = Environment(
    size=ENVIRONMENT_SIZE,
    num_uavs=NUM_UAVS,
    num_targets=NUM_TARGETS,
    num_obstacles=NUM_OBSTACLES,
    random_seed=RANDOM_SEED
)


chromosome_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "data",
    "best_chromosome.pkl"
)


with open(
    chromosome_file,
    "rb"
) as file:

    best_chromosome = pickle.load(file)


ga_result = calculate_fitness(
    best_chromosome,
    environment.uav_positions,
    environment.target_positions,
    environment.obstacles
)


rng = np.random.default_rng(
    RANDOM_SEED + 100
)


random_routes = create_random_chromosome(
    NUM_TARGETS,
    NUM_UAVS,
    rng
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
        "Balance Penalty"
    ])

    writer.writerow([
        "Random Baseline",
        random_result["fitness"],
        random_result["total_distance"],
        random_result["collision_count"],
        random_result["balance_penalty"]
    ])

    writer.writerow([
        "Genetic Algorithm",
        ga_result["fitness"],
        ga_result["total_distance"],
        ga_result["collision_count"],
        ga_result["balance_penalty"]
    ])


print()
print("Baseline comparison completed.")
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