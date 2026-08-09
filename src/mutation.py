import random

from src.chromosome import Chromosome


MUTATION_PROBABILITY = 0.15


def exchange_mutation(chromosome):
    routes = [route.copy() for route in chromosome.routes]

    valid_routes = [i for i, route in enumerate(routes) if len(route) >= 2]

    if not valid_routes:
        return Chromosome(routes)

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    i, j = random.sample(range(len(route)), 2)

    route[i], route[j] = route[j], route[i]

    return Chromosome(routes)


def insertion_mutation(chromosome):
    routes = [route.copy() for route in chromosome.routes]

    valid_routes = [i for i, route in enumerate(routes) if len(route) >= 2]

    if not valid_routes:
        return Chromosome(routes)

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    source = random.randrange(len(route))
    target = random.randrange(len(route))

    gene = route.pop(source)
    route.insert(target, gene)

    return Chromosome(routes)


def inversion_mutation(chromosome):
    routes = [route.copy() for route in chromosome.routes]

    valid_routes = [i for i, route in enumerate(routes) if len(route) >= 2]

    if not valid_routes:
        return Chromosome(routes)

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    i, j = sorted(random.sample(range(len(route)), 2))

    route[i:j + 1] = reversed(route[i:j + 1])

    return Chromosome(routes)


def task_reallocation_mutation(chromosome):
    all_targets = []

    for route in chromosome.routes:
        all_targets.extend(route)

    random.shuffle(all_targets)

    num_uavs = len(chromosome.routes)
    total_targets = len(all_targets)

    cut_points = sorted(
        random.sample(
            range(1, total_targets),
            num_uavs - 1
        )
    )

    routes = []
    start = 0

    for end in cut_points + [total_targets]:
        routes.append(all_targets[start:end])
        start = end

    return Chromosome(routes)


def mutate(chromosome, mutation_probability=MUTATION_PROBABILITY):
    if random.random() > mutation_probability:
        return chromosome, "none"

    mutation_type = random.choice([
        "exchange",
        "insertion",
        "inversion",
        "task_reallocation"
    ])

    if mutation_type == "exchange":
        mutated = exchange_mutation(chromosome)

    elif mutation_type == "insertion":
        mutated = insertion_mutation(chromosome)

    elif mutation_type == "inversion":
        mutated = inversion_mutation(chromosome)

    else:
        mutated = task_reallocation_mutation(chromosome)

    return mutated, mutation_type


def mutate_population(
    population,
    mutation_probability=MUTATION_PROBABILITY
):
    mutated_population = []

    for chromosome in population:
        mutated, mutation_type = mutate(
            chromosome,
            mutation_probability
        )

        mutated_population.append(
            (mutated, mutation_type)
        )

    return mutated_population