import os
import sys
import csv
import pickle

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


def run_experiment():

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
        num_uavs=NUM_UAVS
    )

    algorithm = GeneticAlgorithm(
        population=population,
        environment=environment,
        generations=20,
        elite_count=2
    )

    best_chromosome, best_fitness = algorithm.run()

    chromosome_file = os.path.join(
        PROJECT_ROOT,
        "results",
        "data",
        "best_chromosome.pkl"
    )

    os.makedirs(
        os.path.dirname(chromosome_file),
        exist_ok=True
    )

    with open(
        chromosome_file,
        "wb"
    ) as file:

        pickle.dump(
            best_chromosome,
            file
        )

    output_file = os.path.join(
        PROJECT_ROOT,
        "results",
        "data",
        "fitness_history.csv"
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
            "Generation",
            "Best Fitness"
        ])

        for generation, fitness in enumerate(
            algorithm.best_fitness_history,
            start=1
        ):
            writer.writerow([
                generation,
                fitness
            ])

    print()
    print("Experiment completed.")
    print(f"Best fitness: {best_fitness:.2f}")
    print(
        "Best chromosome saved to: "
        "results/data/best_chromosome.pkl"
    )
    print(
        "Fitness history saved to: "
        "results/data/fitness_history.csv"
    )


if __name__ == "__main__":
    run_experiment()