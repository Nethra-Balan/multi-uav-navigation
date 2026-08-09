from src.waypoints import build_collision_aware_path
from src.collision import segment_intersects_obstacle


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

        path = build_collision_aware_path(
            uav_positions[uav_index],
            route,
            target_positions,
            obstacles
        )

        route_collision = False

        for i in range(len(path) - 1):

            start = path[i]
            end = path[i + 1]

            for obstacle in obstacles:

                if segment_intersects_obstacle(
                    start,
                    end,
                    obstacle
                ):
                    total_collisions += 1
                    route_collision = True

        if route_collision:
            routes_with_collision += 1

    return {
        "total_collisions": total_collisions,
        "routes_with_collision": routes_with_collision,
        "collision_free": (
            total_collisions == 0
        )
    }