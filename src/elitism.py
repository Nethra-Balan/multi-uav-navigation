def select_elites(population, fitness_values, elite_count=1):
    ranked = sorted(
        zip(population, fitness_values),
        key=lambda x: x[1]
    )

    return [
        chromosome
        for chromosome, fitness in ranked[:elite_count]
    ]