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
    NUM_OBSTACLES
)

from src.environment import Environment
from src.population import generate_population
from src.genetic_algorithm import GeneticAlgorithm
from src.fitness import calculate_fitness


SEEDS = [
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51
]


results = []


for seed in SEEDS:

    random.seed(seed)

    print()
    print(
        f"Running experiment with seed {seed}"
    )

    environment = Environment(
        size=ENVIRONMENT_SIZE,
        num_uavs=NUM_UAVS,
        num_targets=NUM_TARGETS,
        num_obstacles=NUM_OBSTACLES,
        random_seed=seed
    )

    population = generate_population(
        num_individuals=10,
        num_targets=NUM_TARGETS,
        num_uavs=NUM_UAVS,
        random_seed=seed
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

    fitness_result = calculate_fitness(
        best_chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    results.append(
        {
            "seed": seed,
            "fitness": fitness_result["fitness"],
            "total_distance": fitness_result["total_distance"],
            "collision_count": fitness_result["collision_count"],
            "collision_penalty": fitness_result["collision_penalty"],
            "balance_penalty": fitness_result["balance_penalty"]
        }
    )


fitness_values = [
    result["fitness"]
    for result in results
]

distance_values = [
    result["total_distance"]
    for result in results
]

collision_values = [
    result["collision_count"]
    for result in results
]

collision_penalty_values = [
    result["collision_penalty"]
    for result in results
]

balance_values = [
    result["balance_penalty"]
    for result in results
]


mean_fitness = np.mean(
    fitness_values
)

std_fitness = np.std(
    fitness_values
)

best_fitness = np.min(
    fitness_values
)

worst_fitness = np.max(
    fitness_values
)

mean_distance = np.mean(
    distance_values
)

mean_collisions = np.mean(
    collision_values
)

mean_collision_penalty = np.mean(
    collision_penalty_values
)

mean_balance = np.mean(
    balance_values
)


output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "data",
    "multiple_runs.csv"
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
        "Seed",
        "Fitness",
        "Total Distance",
        "Collision Count",
        "Collision Penalty",
        "Balance Penalty"
    ])

    for result in results:

        writer.writerow([
            result["seed"],
            result["fitness"],
            result["total_distance"],
            result["collision_count"],
            result["collision_penalty"],
            result["balance_penalty"]
        ])


print()
print("Multiple-run experiment completed.")
print()
print(
    f"Mean Fitness          : "
    f"{mean_fitness:.2f}"
)

print(
    f"Std. Deviation        : "
    f"{std_fitness:.2f}"
)

print(
    f"Best Fitness          : "
    f"{best_fitness:.2f}"
)

print(
    f"Worst Fitness         : "
    f"{worst_fitness:.2f}"
)

print(
    f"Mean Total Distance   : "
    f"{mean_distance:.2f}"
)

print(
    f"Mean Collision Count  : "
    f"{mean_collisions:.2f}"
)

print(
    f"Mean Collision Penalty: "
    f"{mean_collision_penalty:.2f}"
)

print(
    f"Mean Balance Penalty  : "
    f"{mean_balance:.2f}"
)

print()
print(
    "Results saved to: "
    "results/data/multiple_runs.csv"
)