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


def generate_detour_waypoint(
    start,
    end,
    obstacle,
    margin=5.0
):
    minimum = obstacle["min"]
    maximum = obstacle["max"]

    candidates = [
        np.array([
            minimum[0] - margin,
            minimum[1] - margin,
            minimum[2]
        ]),

        np.array([
            maximum[0] + margin,
            minimum[1] - margin,
            minimum[2]
        ]),

        np.array([
            minimum[0] - margin,
            maximum[1] + margin,
            minimum[2]
        ]),

        np.array([
            maximum[0] + margin,
            maximum[1] + margin,
            minimum[2]
        ]),

        np.array([
            minimum[0] - margin,
            minimum[1] - margin,
            maximum[2] + margin
        ]),

        np.array([
            maximum[0] + margin,
            minimum[1] - margin,
            maximum[2] + margin
        ]),

        np.array([
            minimum[0] - margin,
            maximum[1] + margin,
            maximum[2] + margin
        ]),

        np.array([
            maximum[0] + margin,
            maximum[1] + margin,
            maximum[2] + margin
        ])
    ]

    valid_candidates = []

    for candidate in candidates:

        first_segment_clear = not segment_intersects_obstacle(
            start,
            candidate,
            obstacle
        )

        second_segment_clear = not segment_intersects_obstacle(
            candidate,
            end,
            obstacle
        )

        if first_segment_clear and second_segment_clear:
            distance = (
                np.linalg.norm(candidate - start)
                + np.linalg.norm(end - candidate)
            )

            valid_candidates.append(
                (distance, candidate)
            )

    if not valid_candidates:
        return None

    valid_candidates.sort(
        key=lambda item: item[0]
    )

    return valid_candidates[0][1]


def build_collision_aware_path(
    start,
    target_indices,
    target_positions,
    obstacles
):
    path = [start]

    current_position = start

    for target_index in target_indices:

        target = target_positions[target_index - 1]

        waypoint_added = False

        for obstacle in obstacles:

            if segment_intersects_obstacle(
                current_position,
                target,
                obstacle
            ):

                waypoint = generate_detour_waypoint(
                    current_position,
                    target,
                    obstacle
                )

                if waypoint is not None:
                    path.append(waypoint)
                    current_position = waypoint
                    waypoint_added = True
                    break

        path.append(target)
        current_position = target

    return path