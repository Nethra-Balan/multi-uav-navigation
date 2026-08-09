import os
import sys
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
from src.fitness import calculate_fitness


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

best_chromosome, best_fitness = algorithm.run()

fitness_result = calculate_fitness(
    best_chromosome,
    environment.uav_positions,
    environment.target_positions,
    environment.obstacles
)


routes = best_chromosome.routes

all_targets = []

for route in routes:
    all_targets.extend(route)


correct_uav_count = (
    len(routes) == NUM_UAVS
)

correct_target_count = (
    len(all_targets) == NUM_TARGETS
)

all_targets_present = (
    set(all_targets)
    == set(range(1, NUM_TARGETS + 1))
)

no_duplicates = (
    len(set(all_targets))
    == NUM_TARGETS
)

no_empty_routes = all(
    len(route) > 0
    for route in routes
)


solution_valid = (
    correct_uav_count
    and correct_target_count
    and all_targets_present
    and no_duplicates
    and no_empty_routes
)


print()
print("FINAL SOLUTION VALIDATION")
print("=========================")
print()

print(
    f"Number of UAV routes : "
    f"{len(routes)}"
)

print(
    f"Number of targets    : "
    f"{len(all_targets)}"
)

print()

for index, route in enumerate(routes):

    print(
        f"UAV {index + 1}: "
        f"{route}"
    )

print()

print(
    f"Correct UAV count    : "
    f"{correct_uav_count}"
)

print(
    f"Correct target count : "
    f"{correct_target_count}"
)

print(
    f"All targets present  : "
    f"{all_targets_present}"
)

print(
    f"No duplicate targets : "
    f"{no_duplicates}"
)

print(
    f"No empty routes      : "
    f"{no_empty_routes}"
)

print()

print(
    f"Total distance       : "
    f"{fitness_result['total_distance']:.2f}"
)

print(
    f"Collision count      : "
    f"{fitness_result['collision_count']}"
)

print(
    f"Collision penalty    : "
    f"{fitness_result['collision_penalty']:.2f}"
)

print(
    f"Balance penalty      : "
    f"{fitness_result['balance_penalty']:.2f}"
)

print(
    f"Final fitness        : "
    f"{fitness_result['fitness']:.2f}"
)

print()

if solution_valid:
    print(
        "FINAL SOLUTION STATUS: VALID"
    )
else:
    print(
        "FINAL SOLUTION STATUS: INVALID"
    )