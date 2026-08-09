import random
from src.chromosome import Chromosome


def generate_population(
    num_individuals,
    num_targets,
    num_uavs,
    random_seed=None
):
    population = []

    rng = random.Random(
        random_seed
    )

    for _ in range(num_individuals):

        targets = list(
            range(1, num_targets + 1)
        )

        rng.shuffle(
            targets
        )

        cut_points = sorted(
            rng.sample(
                range(1, num_targets),
                num_uavs - 1
            )
        )

        routes = []

        start = 0

        for end in cut_points + [num_targets]:

            route = targets[start:end]

            rng.shuffle(
                route
            )

            routes.append(
                route
            )

            start = end

        population.append(
            Chromosome(routes)
        )

    return population