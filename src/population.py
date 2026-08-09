import random
from src.chromosome import Chromosome


def generate_population(num_individuals, num_targets, num_uavs):
    population = []

    for _ in range(num_individuals):
        targets = list(range(1, num_targets + 1))
        random.shuffle(targets)

        cut_points = sorted(
            random.sample(range(1, num_targets), num_uavs - 1)
        )

        routes = []
        start = 0

        for end in cut_points + [num_targets]:
            route = targets[start:end]
            random.shuffle(route)
            routes.append(route)
            start = end

        population.append(Chromosome(routes))

    return population