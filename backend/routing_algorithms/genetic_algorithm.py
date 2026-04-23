"""Genetic Algorithm for TSP/VRP route optimization"""
import random
from typing import List, Tuple
from copy import deepcopy

class GeneticOptimizer:
    def __init__(self, population_size: int = 50, generations: int = 100,
                 mutation_rate: float = 0.1, elite_size: int = 5):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

    def optimize(self, distance_matrix: List[List[float]],
                 start_index: int = 0) -> Tuple[List[int], float]:
        """
        Optimize route using genetic algorithm.

        Returns: (best_route, total_distance)
        """
        n = len(distance_matrix)
        if n <= 1:
            return list(range(n)), 0

        # Initialize population
        population = self._create_initial_population(n, start_index)

        best_route = None
        best_distance = float('inf')

        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = [(self._evaluate(route, distance_matrix), route)
                            for route in population]
            fitness_scores.sort(key=lambda x: x[0])

            # Track best
            if fitness_scores[0][0] < best_distance:
                best_distance = fitness_scores[0][0]
                best_route = deepcopy(fitness_scores[0][1])

            # Selection - keep elite
            elite = [route for _, route in fitness_scores[:self.elite_size]]

            # Create new population
            new_population = elite.copy()

            # Crossover + mutation
            while len(new_population) < self.population_size:
                parent1 = self._tournament_select(population, fitness_scores)
                parent2 = self._tournament_select(population, fitness_scores)
                child = self._crossover(parent1, parent2)

                if random.random() < self.mutation_rate:
                    child = self._mutate(child, n)

                new_population.append(child)

            population = new_population

        return best_route, best_distance

    def _create_initial_population(self, n: int, start: int) -> List[List[int]]:
        """Create random initial routes."""
        population = []
        for _ in range(self.population_size):
            route = [start] + [i for i in range(n) if i != start]
            random.shuffle(route)
            population.append(route)
        return population

    def _evaluate(self, route: List[int], dist_matrix: List[List[float]]) -> float:
        """Calculate total distance for a route."""
        total = 0
        for i in range(len(route) - 1):
            total += dist_matrix[route[i]][route[i+1]]
        return total

    def _tournament_select(self, population: List[List[int]],
                          fitness_scores: List[Tuple[float, List[int]]]) -> List[int]:
        """Tournament selection."""
        k = 3
        selected = random.sample(fitness_scores, min(k, len(fitness_scores)))
        return min(selected, key=lambda x: x[0])[1]

    def _crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """Order crossover (OX) for preserving order."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start:end+1] = parent1[start:end+1]

        # Fill remaining with parent2's order
        parent2_remaining = [i for i in parent2 if i not in child]
        idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = parent2_remaining[idx]
                idx += 1
        return child

    def _mutate(self, route: List[int], n: int) -> List[int]:
        """Swap mutation."""
        if len(route) < 2:
            return route
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
        return route


def genetic_tsp(distance_matrix: List[List[float]],
                start_index: int = 0,
                population_size: int = 50,
                generations: int = 100) -> Tuple[List[int], float]:
    """Convenience function for genetic TSP."""
    optimizer = GeneticOptimizer(population_size=population_size,
                                 generations=generations)
    return optimizer.optimize(distance_matrix, start_index)