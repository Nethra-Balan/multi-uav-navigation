import matplotlib.pyplot as plt


def plot_environment(environment):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

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
            alpha=0.3
        )

    start_positions = environment.uav_positions

    ax.scatter(
        start_positions[:, 0],
        start_positions[:, 1],
        start_positions[:, 2],
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
        s=30,
        label="Targets"
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.depth)
    ax.set_zlim(0, environment.height)

    ax.set_title("3D Multi-UAV Environment")

    ax.legend()

    plt.show()


def plot_optimized_paths(environment, chromosome):
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

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

    targets = environment.target_positions

    ax.scatter(
        targets[:, 0],
        targets[:, 1],
        targets[:, 2],
        marker="o",
        s=25,
        label="Targets"
    )

    for uav_index, route in enumerate(chromosome.routes):

        start = environment.uav_positions[uav_index]

        points = [start]

        for target_index in route:
            points.append(
                targets[target_index - 1]
            )

        points = list(points)

        x_values = [point[0] for point in points]
        y_values = [point[1] for point in points]
        z_values = [point[2] for point in points]

        ax.plot(
            x_values,
            y_values,
            z_values,
            marker="o",
            linewidth=2,
            label=f"UAV {uav_index + 1}"
        )

        ax.scatter(
            start[0],
            start[1],
            start[2],
            marker="^",
            s=80
        )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    ax.set_xlim(0, environment.width)
    ax.set_ylim(0, environment.depth)
    ax.set_zlim(0, environment.height)

    ax.set_title(
        "Optimized Multi-UAV 3D Path Planning"
    )

    ax.legend()

    plt.show()