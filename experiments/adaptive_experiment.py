import os
import sys
import csv

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
from src.adaptive_genetic_algorithm import (
    AdaptiveGeneticAlgorithm
)


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

    algorithm = AdaptiveGeneticAlgorithm(
        population=population,
        environment=environment,
        generations=30,
        elite_count=2
    )

    best_chromosome, best_fitness = (
        algorithm.run()
    )

    output_file = os.path.join(
        PROJECT_ROOT,
        "results",
        "data",
        "adaptive_fitness_history.csv"
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
            "Best Fitness",
            "Mutation Probability"
        ])

        for generation, (
            fitness,
            mutation_probability
        ) in enumerate(
            zip(
                algorithm.best_fitness_history,
                algorithm.mutation_history
            ),
            start=1
        ):

            writer.writerow([
                generation,
                fitness,
                mutation_probability
            ])

    print()
    print(
        "Adaptive experiment completed."
    )

    print(
        f"Best fitness: "
        f"{best_fitness:.2f}"
    )

    print(
        "Fitness history saved to: "
        "results/data/"
        "adaptive_fitness_history.csv"
    )


if __name__ == "__main__":
    run_experiment()