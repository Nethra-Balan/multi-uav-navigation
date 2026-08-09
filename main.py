from config import (
    ENVIRONMENT_SIZE,
    NUM_UAVS,
    NUM_TARGETS,
    NUM_OBSTACLES,
    RANDOM_SEED
)

from src.environment import Environment
from src.visualization import plot_environment


def main():
    environment = Environment(
        size=ENVIRONMENT_SIZE,
        num_uavs=NUM_UAVS,
        num_targets=NUM_TARGETS,
        num_obstacles=NUM_OBSTACLES,
        random_seed=RANDOM_SEED
    )

    plot_environment(environment)
    for i, target in enumerate(environment.target_positions):
        for obstacle in environment.obstacles:
            if environment._is_point_inside_obstacle(target, obstacle):
                print("Invalid target:", i + 1, target)


if __name__ == "__main__":
    main()