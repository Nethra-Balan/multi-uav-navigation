import numpy as np


def euclidean_distance(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)

    return np.linalg.norm(point1 - point2)


def calculate_route_distance(route, start_position, target_positions):
    if not route:
        return 0.0

    distance = 0.0
    current_position = start_position

    for target_id in route:
        target_position = target_positions[target_id - 1]

        distance += euclidean_distance(
            current_position,
            target_position
        )

        current_position = target_position

    distance += euclidean_distance(
        current_position,
        start_position
    )

    return distance


def calculate_total_distance(chromosome, start_positions, target_positions):
    total_distance = 0.0
    route_distances = []

    for uav_index, route in enumerate(chromosome.routes):
        distance = calculate_route_distance(
            route,
            start_positions[uav_index],
            target_positions
        )

        route_distances.append(distance)
        total_distance += distance

    return total_distance, route_distances


def segment_intersects_obstacle(point1, point2, obstacle):
    minimum = obstacle["min"]
    maximum = obstacle["max"]

    direction = point2 - point1

    t_min = 0.0
    t_max = 1.0

    for axis in range(3):
        if abs(direction[axis]) < 1e-10:
            if point1[axis] < minimum[axis] or point1[axis] > maximum[axis]:
                return False
        else:
            t1 = (minimum[axis] - point1[axis]) / direction[axis]
            t2 = (maximum[axis] - point1[axis]) / direction[axis]

            if t1 > t2:
                t1, t2 = t2, t1

            t_min = max(t_min, t1)
            t_max = min(t_max, t2)

            if t_min > t_max:
                return False

    return True


def route_has_collision(route, start_position, target_positions, obstacles):
    if not route:
        return False

    current_position = np.array(start_position)

    for target_id in route:
        target_position = np.array(target_positions[target_id - 1])

        for obstacle in obstacles:
            if segment_intersects_obstacle(
                current_position,
                target_position,
                obstacle
            ):
                return True

        current_position = target_position

    for obstacle in obstacles:
        if segment_intersects_obstacle(
            current_position,
            np.array(start_position),
            obstacle
        ):
            return True

    return False


def calculate_collision_penalty(
    chromosome,
    start_positions,
    target_positions,
    obstacles
):
    collision_count = 0
    collision_penalty = 0.0

    for uav_index, route in enumerate(chromosome.routes):
        if route_has_collision(
            route,
            start_positions[uav_index],
            target_positions,
            obstacles
        ):
            collision_count += 1

            route_distance = calculate_route_distance(
                route,
                start_positions[uav_index],
                target_positions
            )

            collision_penalty += 5.0 * route_distance

    return collision_count, collision_penalty