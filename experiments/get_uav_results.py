import os
import sys
import pickle

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
    NUM_OBSTACLES,
    RANDOM_SEED
)

from src.environment import Environment
from src.fitness import calculate_fitness


def main():

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

    with open(chromosome_file, "rb") as file:
        best_chromosome = pickle.load(file)

    result = calculate_fitness(
        best_chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    print("\nFINAL UAV PATH RESULTS")
    print("======================")

    for i, distance in enumerate(
        result["route_distances"],
        start=1
    ):
        print(
            f"UAV {i}: "
            f"{distance:.2f} m | "
            f"Targets: {len(best_chromosome.routes[i - 1])}"
        )

    print()
    print(
        f"Total Path Length: "
        f"{result['total_distance']:.2f} m"
    )

    print(
        f"Task Balance (Std. Deviation): "
        f"{result['balance_penalty']:.2f} m"
    )

    print(
        f"Collision Count: "
        f"{result['collision_count']}"
    )

    print(
        f"Final Fitness: "
        f"{result['fitness']:.2f}"
    )


if __name__ == "__main__":
    main()