"""Algorithm Router - Dynamic algorithm selection based on scenario"""
from enum import Enum
from dataclasses import dataclass


class AlgorithmType(Enum):
    DIJKSTRA = "dijkstra"
    ASTAR = "astar"
    BFS = "bfs"
    DFS = "dfs"
    GREEDY = "greedy"
    FLOYD_WARSHALL = "floyd_warshall"
    GENETIC = "genetic"


@dataclass
class ScenarioParams:
    traffic_density: float  # 0.0-2.0
    num_drivers: int
    num_orders: int
    is_urgent: bool
    graph_size: int
    is_rush_hour: bool


def select_algorithm(params: ScenarioParams, mode: str = "dynamic") -> AlgorithmType:
    """
    Select optimal algorithm based on scenario parameters.

    When mode == 'dynamic': Auto-select based on params
    When mode == 'manual': Return DIJKSTRA (user selects manually)
    """
    if mode != "dynamic":
        return AlgorithmType.DIJKSTRA

    # High urgency + rush hour -> Greedy Best-First
    if params.is_urgent and params.is_rush_hour:
        return AlgorithmType.GREEDY

    # High traffic + many orders -> A* (heuristic helps)
    if params.traffic_density > 1.5 and params.num_orders > 100:
        return AlgorithmType.ASTAR

    # Small graph / debug mode -> BFS
    if params.graph_size < 100:
        return AlgorithmType.BFS

    # Large batch optimization -> Genetic Algorithm
    if params.num_orders > 500:
        return AlgorithmType.GENETIC

    # Default: Dijkstra (reliable, optimal)
    return AlgorithmType.DIJKSTRA