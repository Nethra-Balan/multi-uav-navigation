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
from src.path_planning import (
    calculate_total_distance,
    calculate_collision_penalty
)


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

    total_distance, route_distances = calculate_total_distance(
        chromosome,
        environment.uav_positions,
        environment.target_positions
    )

    collision_count, collision_penalty = calculate_collision_penalty(
        chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    print("UAV route distances:")

    for i, distance in enumerate(route_distances):
        print(f"UAV {i + 1}: {distance:.2f} m")

    print(f"Total path distance: {total_distance:.2f} m")
    print(f"UAV routes with collision: {collision_count}")
    print(f"Collision penalty: {collision_penalty:.2f}")


if __name__ == "__main__":
    main()