import threading
import time
from typing import Optional

from src.fitness import calculate_fitness
from src.selection import tournament_selection
from src.crossover import crossover_population
from src.crossover import CROSSOVER_PROBABILITY
from src.mutation import mutate_population
from src.mutation import MUTATION_PROBABILITY
from src.elitism import select_elites
from src.integration.engine_events import GenerationCallback, GenerationEvent
from src.fitness import COLLISION_PENALTY, BALANCE_WEIGHT


class GeneticAlgorithm:

    def __init__(
        self,
        population,
        environment,
        generations=20,
        elite_count=2,
        crossover_probability=CROSSOVER_PROBABILITY,
        mutation_probability=MUTATION_PROBABILITY,
        collision_penalty=COLLISION_PENALTY,
        balance_weight=BALANCE_WEIGHT
    ):
        self.population = population
        self.environment = environment
        self.generations = generations
        self.elite_count = elite_count
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.collision_penalty = collision_penalty
        self.balance_weight = balance_weight

        self.best_fitness_history = []
        self.best_chromosome = None
        self.best_fitness = float("inf")

    def evaluate_population(self, population):

        fitness_values = []

        for chromosome in population:

            result = calculate_fitness(
                chromosome,
                self.environment.uav_positions,
                self.environment.target_positions,
                self.environment.obstacles,
                self.collision_penalty,
                self.balance_weight
            )

            fitness_values.append(result["fitness"])

        return fitness_values

    def run_generation(
        self,
        generation: int,
        callback: Optional[GenerationCallback] = None
    ) -> GenerationEvent:
        fitness_values = self.evaluate_population(self.population)

        best_index = fitness_values.index(min(fitness_values))
        generation_best_fitness = fitness_values[best_index]

        if generation_best_fitness < self.best_fitness:
            self.best_fitness = generation_best_fitness
            self.best_chromosome = self.population[best_index]

        self.best_fitness_history.append(self.best_fitness)

        best_result = calculate_fitness(
            self.best_chromosome,
            self.environment.uav_positions,
            self.environment.target_positions,
            self.environment.obstacles,
            self.collision_penalty,
            self.balance_weight,
        )

        print(
            f"Generation {generation}: "
            f"Best Fitness = {self.best_fitness:.2f}"
        )

        elites = select_elites(
            self.population,
            fitness_values,
            elite_count=self.elite_count
        )

        selected = tournament_selection(
            self.population,
            num_selected=len(self.population),
            start_positions=self.environment.uav_positions,
            target_positions=self.environment.target_positions,
            obstacles=self.environment.obstacles,
            collision_penalty_weight=self.collision_penalty,
            balance_weight=self.balance_weight
        )

        children = crossover_population(
            selected,
            crossover_probability=self.crossover_probability
        )

        mutated_population = mutate_population(
            children,
            mutation_probability=self.mutation_probability
        )

        next_generation = [
            chromosome
            for chromosome, mutation_type in mutated_population
        ]
        next_generation[:self.elite_count] = elites
        self.population = next_generation

        event = GenerationEvent(
            generation=generation,
            total_generations=self.generations,
            best_fitness=float(self.best_fitness),
            mean_fitness=float(sum(fitness_values) / len(fitness_values)),
            mutation_probability=float(self.mutation_probability),
            total_path_distance=float(best_result["total_distance"]),
            collision_count=int(best_result["collision_count"]),
            balance_penalty=float(best_result["balance_penalty"]),
            route_distances=[
                float(distance)
                for distance in best_result["route_distances"]
            ],
            target_counts=[
                len(route)
                for route in self.best_chromosome.routes
            ],
            best_chromosome=self.best_chromosome,
            best_routes=[
                [int(target_id) for target_id in route]
                for route in self.best_chromosome.routes
            ],
            best_fitness_result=best_result,
        )

        if callback is not None:
            callback(event)

        return event

    def run(
        self,
        callback: Optional[GenerationCallback] = None,
        pause_event: Optional[threading.Event] = None,
        stop_event: Optional[threading.Event] = None
    ):
        for generation in range(1, self.generations + 1):
            if stop_event is not None and stop_event.is_set():
                break
            if pause_event is not None:
                while pause_event.is_set():
                    if stop_event is not None and stop_event.is_set():
                        return self.best_chromosome, self.best_fitness
                    time.sleep(0.05)

            self.run_generation(generation, callback)

        return self.best_chromosome, self.best_fitness