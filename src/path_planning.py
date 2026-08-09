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