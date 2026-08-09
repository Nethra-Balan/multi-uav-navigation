import os
import sys
import pickle

import numpy as np
import matplotlib.pyplot as plt


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


chromosome_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "data",
    "best_chromosome.pkl"
)

output_file = os.path.join(
    PROJECT_ROOT,
    "results",
    "figures",
    "uav_routes.png"
)


environment = Environment(
    size=ENVIRONMENT_SIZE,
    num_uavs=NUM_UAVS,
    num_targets=NUM_TARGETS,
    num_obstacles=NUM_OBSTACLES,
    random_seed=RANDOM_SEED
)


with open(
    chromosome_file,
    "rb"
) as file:

    best_chromosome = pickle.load(file)


fig = plt.figure(
    figsize=(10, 8)
)

ax = fig.add_subplot(
    111,
    projection="3d"
)


for obstacle in environment.obstacles:

    minimum = obstacle["min"]
    maximum = obstacle["max"]

    x = minimum[0]
    y = minimum[1]
    z = minimum[2]

    dx = maximum[0] - minimum[0]
    dy = maximum[1] - minimum[1]
    dz = maximum[2] - minimum[2]

    ax.bar3d(
        x,
        y,
        z,
        dx,
        dy,
        dz,
        alpha=0.25
    )


target_positions = environment.target_positions


ax.scatter(
    target_positions[:, 0],
    target_positions[:, 1],
    target_positions[:, 2],
    marker="o",
    s=50,
    label="Targets"
)


start_position = environment.start_position


ax.scatter(
    start_position[0],
    start_position[1],
    start_position[2],
    marker="*",
    s=150,
    label="UAV Start"
)


for target_index, position in enumerate(
    target_positions,
    start=1
):

    ax.text(
        position[0],
        position[1],
        position[2],
        f"T{target_index}",
        fontsize=8
    )


for uav_index, route in enumerate(
    best_chromosome.routes,
    start=1
):

    route_positions = [
        start_position
    ]

    for target in route:

        target_position = target_positions[
            target - 1
        ]

        route_positions.append(
            target_position
        )

    route_positions = np.array(
        route_positions
    )

    ax.plot(
        route_positions[:, 0],
        route_positions[:, 1],
        route_positions[:, 2],
        marker="o",
        linewidth=2,
        label=f"UAV {uav_index}"
    )


ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

ax.set_title(
    "Optimized UAV Routes using Genetic Algorithm"
)

ax.set_xlim(
    0,
    ENVIRONMENT_SIZE[0]
)

ax.set_ylim(
    0,
    ENVIRONMENT_SIZE[1]
)

ax.set_zlim(
    0,
    ENVIRONMENT_SIZE[2]
)

ax.legend()

plt.tight_layout()


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)

plt.savefig(
    output_file,
    dpi=300
)

plt.show()

print(
    "Route visualization saved to: "
    "results/figures/uav_routes.png"
)