import random

from src.chromosome import Chromosome


CROSSOVER_PROBABILITY = 0.85


def flatten_routes(chromosome):
    genes = []

    for route in chromosome.routes:
        genes.extend(route)

    return genes


def split_routes(genes, num_uavs):
    total_targets = len(genes)

    cut_points = sorted(
        random.sample(
            range(1, total_targets),
            num_uavs - 1
        )
    )

    routes = []
    start = 0

    for end in cut_points + [total_targets]:
        routes.append(genes[start:end])
        start = end

    return routes


def order_crossover(parent1, parent2):
    genes1 = flatten_routes(parent1)
    genes2 = flatten_routes(parent2)

    length = len(genes1)

    start, end = sorted(
        random.sample(range(length), 2)
    )

    child_genes = [None] * length

    child_genes[start:end] = genes1[start:end]

    remaining_genes = [
        gene for gene in genes2
        if gene not in child_genes
    ]

    position = 0

    for i in range(length):
        if child_genes[i] is None:
            child_genes[i] = remaining_genes[position]
            position += 1

    routes = split_routes(
        child_genes,
        len(parent1.routes)
    )

    return Chromosome(routes)


def crossover_population(
    selected_population,
    crossover_probability=CROSSOVER_PROBABILITY
):
    children = []

    population_size = len(selected_population)

    for i in range(0, population_size, 2):
        parent1 = selected_population[i]

        if i + 1 < population_size:
            parent2 = selected_population[i + 1]
        else:
            parent2 = selected_population[0]

        if random.random() < crossover_probability:
            child1 = order_crossover(parent1, parent2)
            child2 = order_crossover(parent2, parent1)

            children.extend([child1, child2])
        else:
            children.extend([parent1, parent2])

    return children[:population_size]