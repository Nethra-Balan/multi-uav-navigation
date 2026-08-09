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

    chromosome = population[0]

    result = calculate_fitness(
        chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    print("UAV route distances:")

    for i, distance in enumerate(result["route_distances"]):
        print(f"UAV {i + 1}: {distance:.2f} m")

    print(f"Total path distance: {result['total_distance']:.2f} m")
    print(f"UAV routes with collision: {result['collision_count']}")
    print(f"Collision penalty: {result['collision_penalty']:.2f}")
    print(f"Task balance: {result['task_balance']:.2f} m")
    print(f"Task balance penalty: {result['balance_penalty']:.2f}")
    print(f"Final fitness: {result['fitness']:.2f}")


if __name__ == "__main__":
    main()