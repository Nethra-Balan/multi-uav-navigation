class Chromosome:
    def __init__(self, routes):
        self.routes = routes
        self.fitness = None

    def get_all_targets(self):
        targets = []

        for route in self.routes:
            targets.extend(route)

        return targets

    def is_valid(self, num_targets, num_uavs):
        if len(self.routes) != num_uavs:
            return False

        if any(len(route) == 0 for route in self.routes):
            return False

        targets = self.get_all_targets()

        if len(targets) != num_targets:
            return False

        if set(targets) != set(range(1, num_targets + 1)):
            return False

        if len(set(targets)) != num_targets:
            return False

        return True