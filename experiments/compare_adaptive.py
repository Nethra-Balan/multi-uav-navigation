import os
import sys
import csv
import random
import copy
import numpy as np

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)

from config import (
    ENVIRONMENT_SIZE,
    NUM_UAVS,
    NUM_TARGETS,
    NUM_OBSTACLES
)

from src.environment import Environment
from src.population import generate_population
from src.genetic_algorithm import GeneticAlgorithm
from src.adaptive_genetic_algorithm import (
    AdaptiveGeneticAlgorithm
)


NUM_RUNS = 10
GENERATIONS = 30
POPULATION_SIZE = 10
ELITE_COUNT = 2


def run_comparison():

    original_results = []
    adaptive_results = []

    for seed in range(1, NUM_RUNS + 1):

        random.seed(seed)
        np.random.seed(seed)

        environment = Environment(
            size=ENVIRONMENT_SIZE,
            num_uavs=NUM_UAVS,
            num_targets=NUM_TARGETS,
            num_obstacles=NUM_OBSTACLES,
            random_seed=seed
        )

        population = generate_population(
            num_individuals=POPULATION_SIZE,
            num_targets=NUM_TARGETS,
            num_uavs=NUM_UAVS
        )

        original_population = copy.deepcopy(
            population
        )

        adaptive_population = copy.deepcopy(
            population
        )

        random.seed(seed)

        original_algorithm = GeneticAlgorithm(
            population=original_population,
            environment=environment,
            generations=GENERATIONS,
            elite_count=ELITE_COUNT
        )

        _, original_fitness = (
            original_algorithm.run()
        )

        random.seed(seed)

        adaptive_algorithm = (
            AdaptiveGeneticAlgorithm(
                population=adaptive_population,
                environment=environment,
                generations=GENERATIONS,
                elite_count=ELITE_COUNT
            )
        )

        _, adaptive_fitness = (
            adaptive_algorithm.run()
        )

        original_results.append(
            original_fitness
        )

        adaptive_results.append(
            adaptive_fitness
        )

        print(
            f"Run {seed}: "
            f"Original = {original_fitness:.2f}, "
            f"Adaptive = {adaptive_fitness:.2f}"
        )

    original_mean = np.mean(
        original_results
    )

    original_std = np.std(
        original_results
    )

    adaptive_mean = np.mean(
        adaptive_results
    )

    adaptive_std = np.std(
        adaptive_results
    )

    original_best = np.min(
        original_results
    )

    adaptive_best = np.min(
        adaptive_results
    )

    original_worst = np.max(
        original_results
    )

    adaptive_worst = np.max(
        adaptive_results
    )

    print()
    print("ADAPTIVE MUTATION COMPARISON")
    print("============================")

    print(
        f"Original GA Mean Fitness   : "
        f"{original_mean:.2f}"
    )

    print(
        f"Original GA Std. Deviation : "
        f"{original_std:.2f}"
    )

    print(
        f"Original GA Best Fitness   : "
        f"{original_best:.2f}"
    )

    print(
        f"Original GA Worst Fitness  : "
        f"{original_worst:.2f}"
    )

    print()

    print(
        f"Adaptive GA Mean Fitness   : "
        f"{adaptive_mean:.2f}"
    )

    print(
        f"Adaptive GA Std. Deviation : "
        f"{adaptive_std:.2f}"
    )

    print(
        f"Adaptive GA Best Fitness   : "
        f"{adaptive_best:.2f}"
    )

    print(
        f"Adaptive GA Worst Fitness  : "
        f"{adaptive_worst:.2f}"
    )

    improvement = (
        (
            original_mean
            - adaptive_mean
        )
        / original_mean
    ) * 100

    print()

    print(
        f"Mean Fitness Improvement   : "
        f"{improvement:.2f}%"
    )

    output_file = os.path.join(
        PROJECT_ROOT,
        "results",
        "data",
        "adaptive_comparison.csv"
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
            "Run",
            "Original GA",
            "Adaptive GA"
        ])

        for i in range(NUM_RUNS):

            writer.writerow([
                i + 1,
                original_results[i],
                adaptive_results[i]
            ])

    print()
    print(
        "Comparison results saved to: "
        "results/data/adaptive_comparison.csv"
    )


if __name__ == "__main__":
    run_comparison()