from config import (
    ENVIRONMENT_SIZE,
    NUM_UAVS,
    NUM_TARGETS,
    NUM_OBSTACLES,
    RANDOM_SEED
)

from src.environment import Environment
from src.visualization import (
    plot_environment,
    plot_optimized_paths
)
from src.population import generate_population
from src.genetic_algorithm import GeneticAlgorithm
from src.path_validation import validate_chromosome
from src.waypoints import build_collision_aware_path


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

    print("\nTesting collision-aware waypoint generation...")

    test_route = population[0].routes[0]

    test_path = build_collision_aware_path(
        environment.uav_positions[0],
        test_route,
        environment.target_positions,
        environment.obstacles
    )

    print("\nTest target route:")
    print(test_route)

    print("\nCollision-aware test path:")

    for i, point in enumerate(test_path):
        print(
            f"Point {i + 1}: "
            f"[{point[0]:.2f}, "
            f"{point[1]:.2f}, "
            f"{point[2]:.2f}]"
        )

    print(
        "\nOriginal targets in route:",
        len(test_route)
    )

    print(
        "Points including start and waypoints:",
        len(test_path)
    )

    genetic_algorithm = GeneticAlgorithm(
        population=population,
        environment=environment,
        generations=20,
        elite_count=2
    )

    best_chromosome, best_fitness = genetic_algorithm.run()

    print("\nOptimization completed.")

    print(
        f"Best fitness: {best_fitness:.2f}"
    )

    print("\nBest chromosome routes:")

    for i, route in enumerate(
        best_chromosome.routes
    ):
        print(
            f"UAV {i + 1}: {route}"
        )

    print(
        "\nValid best chromosome:",
        best_chromosome.is_valid(
            NUM_TARGETS,
            NUM_UAVS
        )
    )

    validation = validate_chromosome(
        best_chromosome,
        environment.uav_positions,
        environment.target_positions,
        environment.obstacles
    )

    print("\nFinal Path Validation")

    print(
        "Total collisions:",
        validation["total_collisions"]
    )

    print(
        "Routes with collision:",
        validation["routes_with_collision"]
    )

    print(
        "Collision-free solution:",
        validation["collision_free"]
    )

    print("\nDisplaying optimized paths...")

    plot_optimized_paths(
        environment,
        best_chromosome
    )


if __name__ == "__main__":
    main()