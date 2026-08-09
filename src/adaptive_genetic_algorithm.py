from src.fitness import calculate_fitness
from src.selection import tournament_selection
from src.crossover import crossover_population
from src.adaptive_mutation import (
    get_mutation_probability,
    mutate_population
)
from src.elitism import select_elites


class AdaptiveGeneticAlgorithm:

    def __init__(
        self,
        population,
        environment,
        generations=30,
        elite_count=2
    ):
        self.population = population
        self.environment = environment
        self.generations = generations
        self.elite_count = elite_count

        self.best_fitness_history = []
        self.mutation_history = []

        self.best_chromosome = None
        self.best_fitness = float("inf")

    def evaluate_population(self, population):

        fitness_values = []

        for chromosome in population:

            result = calculate_fitness(
                chromosome,
                self.environment.uav_positions,
                self.environment.target_positions,
                self.environment.obstacles
            )

            fitness_values.append(
                result["fitness"]
            )

        return fitness_values

    def run(self):

        for generation in range(
            self.generations
        ):

            fitness_values = (
                self.evaluate_population(
                    self.population
                )
            )

            best_index = fitness_values.index(
                min(fitness_values)
            )

            generation_best_fitness = (
                fitness_values[best_index]
            )

            if (
                generation_best_fitness
                < self.best_fitness
            ):

                self.best_fitness = (
                    generation_best_fitness
                )

                self.best_chromosome = (
                    self.population[best_index]
                )

            self.best_fitness_history.append(
                self.best_fitness
            )

            mutation_probability = (
                get_mutation_probability(
                    generation,
                    self.generations
                )
            )

            self.mutation_history.append(
                mutation_probability
            )

            print(
                f"Generation {generation + 1}: "
                f"Best Fitness = "
                f"{self.best_fitness:.2f} | "
                f"Mutation Probability = "
                f"{mutation_probability:.3f}"
            )

            elites = select_elites(
                self.population,
                fitness_values,
                elite_count=self.elite_count
            )

            selected = tournament_selection(
                self.population,
                num_selected=len(
                    self.population
                ),
                start_positions=(
                    self.environment.uav_positions
                ),
                target_positions=(
                    self.environment.target_positions
                ),
                obstacles=(
                    self.environment.obstacles
                )
            )

            children = crossover_population(
                selected
            )

            mutated_population = (
                mutate_population(
                    children,
                    mutation_probability
                )
            )

            next_generation = [
                chromosome
                for chromosome, mutation_type
                in mutated_population
            ]

            next_generation[
                :self.elite_count
            ] = elites

            self.population = next_generation

        return (
            self.best_chromosome,
            self.best_fitness
        )