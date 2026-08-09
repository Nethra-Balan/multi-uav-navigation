import random


MAX_MUTATION_PROBABILITY = 0.30
MIN_MUTATION_PROBABILITY = 0.05


def get_mutation_probability(
    generation,
    total_generations
):
    if total_generations <= 1:
        return MAX_MUTATION_PROBABILITY

    progress = generation / (total_generations - 1)

    probability = (
        MAX_MUTATION_PROBABILITY
        - progress
        * (
            MAX_MUTATION_PROBABILITY
            - MIN_MUTATION_PROBABILITY
        )
    )

    return probability


def exchange_mutation(chromosome):
    routes = [
        route.copy()
        for route in chromosome.routes
    ]

    valid_routes = [
        i
        for i, route in enumerate(routes)
        if len(route) >= 2
    ]

    if not valid_routes:
        return chromosome

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    i, j = random.sample(
        range(len(route)),
        2
    )

    route[i], route[j] = (
        route[j],
        route[i]
    )

    from src.chromosome import Chromosome

    return Chromosome(routes)


def insertion_mutation(chromosome):
    routes = [
        route.copy()
        for route in chromosome.routes
    ]

    valid_routes = [
        i
        for i, route in enumerate(routes)
        if len(route) >= 2
    ]

    if not valid_routes:
        return chromosome

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    source = random.randrange(len(route))
    target = random.randrange(len(route))

    gene = route.pop(source)
    route.insert(target, gene)

    from src.chromosome import Chromosome

    return Chromosome(routes)


def inversion_mutation(chromosome):
    routes = [
        route.copy()
        for route in chromosome.routes
    ]

    valid_routes = [
        i
        for i, route in enumerate(routes)
        if len(route) >= 2
    ]

    if not valid_routes:
        return chromosome

    route_index = random.choice(valid_routes)
    route = routes[route_index]

    i, j = sorted(
        random.sample(
            range(len(route)),
            2
        )
    )

    route[i:j + 1] = reversed(
        route[i:j + 1]
    )

    from src.chromosome import Chromosome

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
        routes.append(
            all_targets[start:end]
        )
        start = end

    from src.chromosome import Chromosome

    return Chromosome(routes)


def mutate(
    chromosome,
    mutation_probability
):
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
        mutated = task_reallocation_mutation(
            chromosome
        )

    return mutated, mutation_type


def mutate_population(
    population,
    mutation_probability
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