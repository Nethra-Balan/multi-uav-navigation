import numpy as np
import matplotlib.pyplot as plt

from src.waypoints import build_collision_aware_path


def draw_obstacle(ax, obstacle, alpha=0.25):
    minimum = obstacle["min"]
    maximum = obstacle["max"]

    x1, y1, z1 = minimum
    x2, y2, z2 = maximum

    vertices = np.array([
        [x1, y1, z1],
        [x2, y1, z1],
        [x2, y2, z1],
        [x1, y2, z1],
        [x1, y1, z2],
        [x2, y1, z2],
        [x2, y2, z2],
        [x1, y2, z2]
    ])

    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[3], vertices[0], vertices[4], vertices[7]]
    ]

    ax.add_collection3d(
        __import__("mpl_toolkits.mplot3d.art3d", fromlist=["Poly3DCollection"]).Poly3DCollection(
            faces,
            alpha=alpha
        )
    )


def plot_environment(environment):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.depth)
    ax.set_zlim(0, environment.height)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_title("Multi-UAV 3D Environment")

    starts = environment.uav_positions

    ax.scatter(
        starts[:, 0],
        starts[:, 1],
        starts[:, 2],
        marker="^",
        s=80,
        label="UAV Start"
    )

    targets = environment.target_positions

    ax.scatter(
        targets[:, 0],
        targets[:, 1],
        targets[:, 2],
        marker="o",
        s=25,
        label="Targets"
    )

    for obstacle in environment.obstacles:
        draw_obstacle(ax, obstacle)

    ax.legend()

    plt.tight_layout()
    plt.show()


def plot_optimized_paths(
    environment,
    chromosome
):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.depth)
    ax.set_zlim(0, environment.height)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_title(
        "Optimized Collision-Free Multi-UAV Paths"
    )

    targets = environment.target_positions

    ax.scatter(
        targets[:, 0],
        targets[:, 1],
        targets[:, 2],
        marker="o",
        s=25,
        label="Targets"
    )

    starts = environment.uav_positions

    ax.scatter(
        starts[:, 0],
        starts[:, 1],
        starts[:, 2],
        marker="^",
        s=100,
        label="UAV Start"
    )

    for obstacle in environment.obstacles:
        draw_obstacle(ax, obstacle)

    for uav_index, route in enumerate(
        chromosome.routes
    ):

        path = build_collision_aware_path(
            starts[uav_index],
            route,
            targets,
            environment.obstacles
        )

        path = np.array(path)

        ax.plot(
            path[:, 0],
            path[:, 1],
            path[:, 2],
            linewidth=2,
            label=f"UAV {uav_index + 1}"
        )

        if len(path) > 2:

            waypoints = path[1:-1]

            ax.scatter(
                waypoints[:, 0],
                waypoints[:, 1],
                waypoints[:, 2],
                marker="x",
                s=40
            )

    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.05, 1)
    )

    plt.tight_layout()
    plt.show()