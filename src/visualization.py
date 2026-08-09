import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def plot_environment(environment):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    start = environment.start_position

    ax.scatter(
        start[0],
        start[1],
        start[2],
        marker="*",
        s=150,
        label="UAV Start"
    )

    targets = environment.target_positions

    ax.scatter(
        targets[:, 0],
        targets[:, 1],
        targets[:, 2],
        marker="o",
        s=30,
        label="Targets"
    )

    for obstacle in environment.obstacles:
        minimum = obstacle["min"]
        maximum = obstacle["max"]

        x1, y1, z1 = minimum
        x2, y2, z2 = maximum

        vertices = [
            [x1, y1, z1],
            [x2, y1, z1],
            [x2, y2, z1],
            [x1, y2, z1],
            [x1, y1, z2],
            [x2, y1, z2],
            [x2, y2, z2],
            [x1, y2, z2]
        ]

        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[0], vertices[3], vertices[7], vertices[4]]
        ]

        ax.add_collection3d(
            Poly3DCollection(
                faces,
                alpha=0.3
            )
        )

    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.depth)
    ax.set_zlim(0, environment.height)

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")

    ax.set_title("Multi-UAV 3D Environment")

    ax.legend()

    plt.show()