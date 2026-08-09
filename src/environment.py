import numpy as np


class Environment:
    def __init__(
        self,
        size,
        num_uavs,
        num_targets,
        num_obstacles,
        random_seed=None
    ):
        self.width, self.depth, self.height = size
        self.num_uavs = num_uavs
        self.num_targets = num_targets
        self.num_obstacles = num_obstacles

        self.rng = np.random.default_rng(random_seed)

        self.start_position = np.array([10.0, 10.0, 10.0])

        self.uav_positions = self._generate_uav_positions()
        self.obstacles = self._generate_obstacles()
        self.target_positions = self._generate_target_positions()

    def _generate_uav_positions(self):
        return np.tile(self.start_position, (self.num_uavs, 1))

    def _generate_target_positions(self):
        targets = []

        while len(targets) < self.num_targets:
            point = np.array([
                self.rng.uniform(20, self.width - 20),
                self.rng.uniform(20, self.depth - 20),
                self.rng.uniform(10, self.height - 10)
            ])

            inside_obstacle = any(
                self._is_point_inside_obstacle(point, obstacle)
                for obstacle in self.obstacles
            )

            if not inside_obstacle:
                targets.append(point)

        return np.array(targets)

    def _generate_obstacles(self):
        obstacles = []

        for _ in range(self.num_obstacles):
            x = self.rng.uniform(20, self.width - 50)
            y = self.rng.uniform(20, self.depth - 50)
            z = 0

            length = self.rng.uniform(15, 30)
            width = self.rng.uniform(15, 30)
            height = self.rng.uniform(20, self.height - 20)

            obstacles.append({
                "min": np.array([x, y, z]),
                "max": np.array([
                    x + length,
                    y + width,
                    z + height
                ])
            })

        return obstacles

    def _is_point_inside_obstacle(self, point, obstacle):
        minimum = obstacle["min"]
        maximum = obstacle["max"]

        return np.all(point >= minimum) and np.all(point <= maximum)