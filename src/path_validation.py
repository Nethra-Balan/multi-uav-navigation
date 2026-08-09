import numpy as np


def segment_intersects_obstacle(start, end, obstacle):
    minimum = obstacle["min"]
    maximum = obstacle["max"]

    direction = end - start

    t_min = 0.0
    t_max = 1.0

    for axis in range(3):

        if abs(direction[axis]) < 1e-12:

            if (
                start[axis] < minimum[axis]
                or start[axis] > maximum[axis]
            ):
                return False

        else:
            t1 = (
                minimum[axis] - start[axis]
            ) / direction[axis]

            t2 = (
                maximum[axis] - start[axis]
            ) / direction[axis]

            if t1 > t2:
                t1, t2 = t2, t1

            t_min = max(t_min, t1)
            t_max = min(t_max, t2)

            if t_min > t_max:
                return False

    return True


def validate_route(
    route,
    start_position,
    target_positions,
    obstacles
):
    points = [start_position]

    for target_index in route:
        points.append(
            target_positions[target_index - 1]
        )

    collision_count = 0

    for i in range(len(points) - 1):

        start = points[i]
        end = points[i + 1]

        for obstacle in obstacles:

            if segment_intersects_obstacle(
                start,
                end,
                obstacle
            ):
                collision_count += 1
                break

    return collision_count


def validate_chromosome(
    chromosome,
    uav_positions,
    target_positions,
    obstacles
):
    total_collisions = 0
    routes_with_collision = 0

    for uav_index, route in enumerate(
        chromosome.routes
    ):

        collisions = validate_route(
            route,
            uav_positions[uav_index],
            target_positions,
            obstacles
        )

        if collisions > 0:
            routes_with_collision += 1

        total_collisions += collisions

    return {
        "total_collisions": total_collisions,
        "routes_with_collision": routes_with_collision,
        "collision_free": total_collisions == 0
    }