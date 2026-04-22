# Food Delivery Optimizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build portfolio-grade food delivery routing system with dynamic algorithm selection, real-time simulation, and premium UI

**Architecture:** Hybrid approach - enhance existing backend, rebuild frontend with premium design. Modular algorithm router for dynamic selection. WebSocket for real-time updates.

**Tech Stack:** Python (FastAPI), React 18 (Vite), Leaflet, Recharts, WebSocket

---

## Phase 1: Backend Core (Tasks 1-12)

### Task 1: Algorithm Router Module
**Files:** Create: `backend/routing/algorithm_router.py`

- [ ] **Step 1: Create routing directory and __init__.py**
```python
# backend/routing/__init__.py
from .algorithm_router import select_algorithm, AlgorithmType

__all__ = ['select_algorithm', 'AlgorithmType']
```

- [ ] **Step 2: Create algorithm_router.py with selection logic**
```python
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
```

- [ ] **Step 3: Run test to verify module imports**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "from backend.routing import select_algorithm, AlgorithmType; print('OK')"
```

- [ ] **Step 4: Commit**
```bash
git add backend/routing/ backend/routing/__init__.py
git commit -m "feat: add algorithm router module with dynamic selection"
```

---

### Task 2: Integrate Algorithm Router into Route Optimizer
**Files:** Modify: `backend/route_optimizer.py:1-30`

- [ ] **Step 1: Update imports to use algorithm router**
```python
# Add after existing imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from routing.algorithm_router import select_algorithm, AlgorithmType
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    AlgorithmType = None
```

- [ ] **Step 2: Run test to verify imports work**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "from backend.route_optimizer import ROUTER_AVAILABLE; print(f'Router: {ROUTER_AVAILABLE}')"
```

- [ ] **Step 3: Commit**
```bash
git add backend/route_optimizer.py
git commit -m "feat: integrate algorithm router into route optimizer"
```

---

### Task 3: Add Genetic Algorithm for Route Optimization
**Files:** Create: `backend/routing/genetic_algorithm.py`

- [ ] **Step 1: Create genetic algorithm module**
```python
"""Genetic Algorithm for TSP/VRP route optimization"""
import random
import heapq
from typing import List, Tuple, Dict
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
```

- [ ] **Step 2: Test genetic algorithm**
```python
# Test with simple distance matrix
test_matrix = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
from backend.routing.genetic_algorithm import genetic_tsp
route, dist = genetic_tsp(test_matrix)
print(f"Route: {route}, Distance: {dist}")  # Should be ~80
```

- [ ] **Step 3: Commit**
```bash
git add backend/routing/genetic_algorithm.py
git commit -m "feat: add genetic algorithm for route optimization"
```

---

### Task 4: Add DFS Algorithm to Routing Module
**Files:** Modify: `backend/routing.py`

- [ ] **Step 1: Add DFS implementation**
```python
def dfs_route(G, source, target):
    """Depth-First Search pathfinding."""
    if source == target:
        return {"path": [source], "path_coords": [get_node_coords(G, source)],
                "total_distance_m": 0, "algorithm": "dfs"}
    
    visited = set()
    stack = [(source, [source], 0)]
    
    while stack:
        node, path, dist = stack.pop()
        
        if node in visited:
            continue
        visited.add(node)
        
        if node == target:
            coords = [get_node_coords(G, n) for n in path]
            return {
                "path": path,
                "path_coords": coords,
                "total_distance_m": dist,
                "algorithm": "dfs"
            }
        
        # Get neighbors sorted by distance (for better paths)
        neighbors = []
        for neighbor in G.neighbors(node):
            if neighbor not in visited:
                edge_data = G.edges[node, neighbor]
                weight = edge_data.get('weight', 1)
                neighbors.append((neighbor, weight))
        
        neighbors.sort(key=lambda x: x[1], reverse=True)  # DFS - explore far first
        
        for neighbor, weight in neighbors:
            if neighbor not in visited:
                new_path = path + [neighbor]
                stack.append((neighbor, new_path, dist + weight))
    
    return {"error": "No path found", "algorithm": "dfs"}
```

- [ ] **Step 2: Add DFS to find_route function dispatch**
```python
# In find_route() function, add to algorithm dispatch:
if algorithm == "dfs":
    return dfs_route(G, source, target)
```

- [ ] **Step 3: Test DFS**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "
from backend.road_network import load_graph
from backend.routing import find_route, get_nearest_node
G = load_graph('Pune, India')
nodes = list(G.nodes())[:10]
if len(nodes) >= 2:
    result = find_route(G, nodes[0], nodes[1], algorithm='dfs')
    print(f'DFS: {result.get(\"algorithm\")}, dist: {result.get(\"total_distance_m\", 0):.0f}m')
"
```

- [ ] **Step 4: Commit**
```bash
git add backend/routing.py
git commit -m "feat: add DFS algorithm to routing module"
```

---

### Task 5: Create Pune Restaurant Data Module
**Files:** Create: `backend/pune_data.py`

- [ ] **Step 1: Create Pune data module with restaurant zones**
```python
"""Pune Restaurant Data Module
Realistic restaurant data for simulation based on actual Pune zones.
"""

PUNE_ZONES = {
    "Kothrud": {
        "center": (18.5113, 73.7797),
        "restaurants": [
            {"name": "Krumbkk", "cuisine": "Bakery", "rating": 4.2},
            {"name": "The Chinese Bowl", "cuisine": "Chinese", "rating": 4.0},
            {"name": "Sharma Sweet House", "cuisine": "Sweets", "rating": 4.3},
            {"name": "Hotel Sukh", "cuisine": "North Indian", "rating": 3.9},
            {"name": "Chaitanya", "cuisine": "Maharashtrian", "rating": 4.1},
            {"name": "Cafe Mondo", "cuisine": "Cafe", "rating": 4.4},
            {"name": "Spice Garden", "cuisine": "Indian", "rating": 4.0},
            {"name": "Bakery Corner", "cuisine": "Bakery", "rating": 4.2},
            {"name": "Urban Burger", "cuisine": "Fast Food", "rating": 3.8},
            {"name": "Pizza Heaven", "cuisine": "Pizza", "rating": 4.1},
            {"name": "Biryani House", "cuisine": "Biryani", "rating": 4.5},
            {"name": "South Spice", "cuisine": "South Indian", "rating": 4.0},
            {"name": "Tandoor King", "cuisine": "Tandoor", "rating": 4.2},
            {"name": "Dragon Express", "cuisine": "Chinese", "rating": 3.9},
            {"name": "Pure Veg", "cuisine": "Vegetarian", "rating": 4.3},
        ]
    },
    "Baner": {
        "center": (18.5647, 73.7719),
        "restaurants": [
            {"name": "Barbeque Nation", "cuisine": "Barbeque", "rating": 4.3},
            {"name": "Maa Lahsun", "cuisine": "North Indian", "rating": 4.1},
            {"name": "The Biryani Life", "cuisine": "Biryani", "rating": 4.4},
            {"name": "Cafe Coffee Day", "cuisine": "Cafe", "rating": 3.9},
            {"name": "Dominos Pizza", "cuisine": "Pizza", "rating": 4.0},
            {"name": "KFC", "cuisine": "Fast Food", "rating": 4.1},
            {"name": "McDonalds", "cuisine": "Fast Food", "rating": 4.0},
            {"name": "Pizza Hut", "cuisine": "Pizza", "rating": 4.2},
            {"name": "Dhangar Kitchen", "cuisine": "Maharashtrian", "rating": 4.3},
            {"name": "Cantonese", "cuisine": "Chinese", "rating": 4.0},
            {"name": "Turmeric", "cuisine": "Indian", "rating": 4.2},
            {"name": "Green Leaf", "cuisine": "Healthy", "rating": 4.1},
            {"name": "Baba Ka Dhaba", "cuisine": "North Indian", "rating": 3.8},
            {"name": "Famous Restaurant", "cuisine": "Multi-cuisine", "rating": 4.0},
        ]
    },
    "Hinjewadi": {
        "center": (18.5907, 73.7383),
        "restaurants": [
            {"name": "Eat India", "cuisine": "Multi-cuisine", "rating": 4.2},
            {"name": "Food Mall", "cuisine": "Food Court", "rating": 3.9},
            {"name": "Pizza King", "cuisine": "Pizza", "rating": 4.0},
            {"name": "Bhelpuri Wala", "cuisine": "Street Food", "rating": 4.1},
            {"name": "Taste of South", "cuisine": "South Indian", "rating": 4.3},
            {"name": "Theobroma", "cuisine": "Bakery", "rating": 4.5},
            {"name": "Cafe 173", "cuisine": "Cafe", "rating": 4.2},
            {"name": "Subway", "cuisine": "Healthy Fast Food", "rating": 4.0},
            {"name": "Freshmenu", "cuisine": "Healthy", "rating": 4.1},
            {"name": "Faasos", "cuisine": "Fast Food", "rating": 4.0},
            {"name": "Behrouz Biryani", "cuisine": "Biryani", "rating": 4.4},
            {"name": "Biryani Blues", "cuisine": "Biryani", "rating": 4.3},
            {"name": "Wow Momo", "cuisine": "Momos", "rating": 4.2},
            {"name": "Burger King", "cuisine": "Fast Food", "rating": 4.1},
            {"name": "Starbucks", "cuisine": "Cafe", "rating": 4.3},
            {"name": "Chaayos", "cuisine": "Cafe", "rating": 4.2},
            {"name": "Crempo", "cuisine": "Bakery", "rating": 4.4},
            {"name": "Nandini", "cuisine": "South Indian", "rating": 4.1},
            {"name": "Madhuram", "cuisine": "South Indian", "rating": 4.0},
            {"name": "Swathi", "cuisine": "South Indian", "rating": 4.3},
        ]
    },
    "Viman Nagar": {
        "center": (18.5679, 73.9100),
        "restaurants": [
            {"name": "Blue Lizard", "cuisine": "Pub Food", "rating": 4.2},
            {"name": "Elephant & Co", "cuisine": "Continental", "rating": 4.4},
            {"name": "Koshy", "cuisine": "South Indian", "rating": 4.0},
            {"name": "German Bakery", "cuisine": "Bakery", "rating": 4.3},
            {"name": "Rainbow Snacks", "cuisine": "Fast Food", "rating": 3.9},
            {"name": "Marrakesh", "cuisine": "Middle Eastern", "rating": 4.2},
            {"name": "Yum Yum Tree", "cuisine": "Chinese", "rating": 4.1},
            {"name": "Rajdhani", "cuisine": "Rajasthani", "rating": 4.2},
            {"name": "Spice Kitchen", "cuisine": "North Indian", "rating": 4.0},
            {"name": "Urban Froth", "cuisine": "Cafe", "rating": 4.3},
            {"name": "Niro", "cuisine": "Cafe", "rating": 4.1},
            {"name": "Baker Street", "cuisine": "Bakery", "rating": 4.2},
            {"name": "Talis", "cuisine": "Continental", "rating": 4.3},
            {"name": "Shizusan", "cuisine": "Asian", "rating": 4.4},
        ]
    },
    "Koregaon Park": {
        "center": (18.5362, 73.8951),
        "restaurants": [
            {"name": "The Flour Works", "cuisine": "Bakery", "rating": 4.5},
            {"name": "Sampan", "cuisine": "Chinese", "rating": 4.3},
            {"name": "Khyde", "cuisine": "Cafe", "rating": 4.4},
            {"name": "Leaping Windows", "cuisine": "Cafe", "rating": 4.2},
            {"name": "Moma", "cuisine": "International", "rating": 4.3},
            {"name": "Shao", "cuisine": "Asian", "rating": 4.4},
            {"name": "Ef Chap", "cuisine": "Thai", "rating": 4.2},
            {"name": "Baker Street", "cuisine": "Bakery", "rating": 4.1},
            {"name": "Dario", "cuisine": "Italian", "rating": 4.3},
            {"name": "Malaka Spice", "cuisine": "Pan Asian", "rating": 4.5},
            {"name": "Paasha", "cuisine": "North Indian", "rating": 4.2},
            {"name": "The Sassy Spoon", "cuisine": "Cafe", "rating": 4.3},
            {"name": "Sula Vineyards", "cuisine": "Fine Dining", "rating": 4.4},
            {"name": "Coreto", "cuisine": "Italian", "rating": 4.1},
            {"name": "Brew", "cuisine": "Cafe", "rating": 4.2},
        ]
    },
    "Wakad": {
        "center": (18.5986, 73.7677),
        "restaurants": [
            {"name": "Mithila", "cuisine": "Maharashtrian", "rating": 4.2},
            {"name": "Vithal Roti", "cuisine": "Maharashtrian", "rating": 4.3},
            {"name": "Kokan Bhakshal", "cuisine": "Maharashtrian", "rating": 4.1},
            {"name": "Cafe Gratitude", "cuisine": "Cafe", "rating": 4.0},
            {"name": "Brahma Kumaris", "cuisine": "Vegetarian", "rating": 4.2},
            {"name": "Shree Krishna", "cuisine": "North Indian", "rating": 4.0},
            {"name": "Maharaja", "cuisine": "North Indian", "rating": 4.1},
            {"name": "Pune Paneer", "cuisine": "North Indian", "rating": 3.9},
            {"name": "Spice 9", "cuisine": "Indian", "rating": 4.0},
            {"name": "99 Dosa", "cuisine": "South Indian", "rating": 4.2},
            {"name": "A2B", "cuisine": "South Indian", "rating": 4.1},
            {"name": "Tiffin Box", "cuisine": "Fast Food", "rating": 3.8},
        ]
    },
    "Hadapsar": {
        "center": (18.5089, 73.9267),
        "restaurants": [
            {"name": "Ganesh Bhel", "cuisine": "Street Food", "rating": 4.2},
            {"name": "Jagtap Dairy", "cuisine": "Dairy", "rating": 4.3},
            {"name": "Ravi Bhel", "cuisine": "Street Food", "rating": 4.1},
            {"name": "Pune Poha", "cuisine": "Maharashtrian", "rating": 4.0},
            {"name": "Shree snacks", "cuisine": "Snacks", "rating": 3.9},
            {"name": "Hotel Sanman", "cuisine": "North Indian", "rating": 4.0},
            {"name": "Garden Restaurant", "cuisine": "Multi-cuisine", "rating": 3.8},
            {"name": "Royal Cafe", "cuisine": "Cafe", "rating": 4.1},
            {"name": "Aroma Kitchen", "cuisine": "Chinese", "rating": 4.0},
            {"name": "Madhuri", "cuisine": "Maharashtrian", "rating": 4.2},
        ]
    }
}

# Traffic congestion zones by time of day
TRAFFIC_ZONES = {
    "morning_rush": {  # 8:00-10:00
        "high_traffic": ["Hinjewadi", "Viman Nagar", "Wakad"],
        "medium_traffic": ["Kothrud", "Baner"],
        "low_traffic": ["Hadapsar", "Koregaon Park"]
    },
    "lunch_rush": {  # 12:00-14:00
        "high_traffic": ["Koregaon Park", "Kothrud", "Hadapsar"],
        "medium_traffic": ["Baner", "Viman Nagar"],
        "low_traffic": ["Hinjewadi", "Wakad"]
    },
    "evening_rush": {  # 18:00-21:00
        "high_traffic": ["Kothrud", "Hinjewadi", "Viman Nagar", "Wakad", "Koregaon Park"],
        "medium_traffic": ["Baner", "Hadapsar"],
        "low_traffic": []
    },
    "night": {  # 22:00-24:00
        "high_traffic": [],
        "medium_traffic": ["Viman Nagar", "Koregaon Park"],
        "low_traffic": ["Kothrud", "Hinjewadi", "Baner", "Wakad", "Hadapsar"]
    },
    "off_peak": {  # Other times
        "high_traffic": [],
        "medium_traffic": ["Kothrud", "Viman Nagar"],
        "low_traffic": ["Hinjewadi", "Baner", "Wakad", "Hadapsar", "Koregaon Park"]
    }
}

def get_time_period(hour: int) -> str:
    """Get time period for traffic simulation."""
    if 8 <= hour < 10:
        return "morning_rush"
    elif 12 <= hour < 14:
        return "lunch_rush"
    elif 18 <= hour < 21:
        return "evening_rush"
    elif 22 <= hour < 24:
        return "night"
    else:
        return "off_peak"

def get_restaurants_by_zone(zone_name: str) -> list:
    """Get all restaurants in a zone."""
    return PUNE_ZONES.get(zone_name, {}).get("restaurants", [])

def get_all_restaurants() -> list:
    """Get all restaurants across all zones."""
    all_restaurants = []
    for zone_name, zone_data in PUNE_ZONES.items():
        for restaurant in zone_data["restaurants"]:
            restaurant["zone"] = zone_name
            restaurant["center_lat"] = zone_data["center"][0]
            restaurant["center_lng"] = zone_data["center"][1]
            all_restaurants.append(restaurant)
    return all_restaurants

def get_traffic_level(zone_name: str, hour: int = 12) -> float:
    """Get traffic multiplier for a zone at given hour.
    
    Returns: traffic level (0.5 = light, 1.0 = normal, 2.0 = heavy)
    """
    period = get_time_period(hour)
    traffic_data = TRAFFIC_ZONES[period]
    
    if zone_name in traffic_data.get("high_traffic", []):
        return 1.8
    elif zone_name in traffic_data.get("medium_traffic", []):
        return 1.3
    else:
        return 0.8

def get_zone_center(zone_name: str) -> tuple:
    """Get center coordinates of a zone."""
    return PUNE_ZONES.get(zone_name, {}).get("center", (18.5204, 73.8567))
```

- [ ] **Step 2: Test Pune data module**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "
from backend.pune_data import get_all_restaurants, get_traffic_level, PUNE_ZONES
print(f'Zones: {len(PUNE_ZONES)}')
print(f'Restaurants: {len(get_all_restaurants())}')
print(f'Hinjewadi traffic at 9am: {get_traffic_level(\"Hinjewadi\", 9)}')
print(f'Hinjewadi traffic at 2pm: {get_traffic_level(\"Hinjewadi\", 14)}')
"
```

- [ ] **Step 3: Commit**
```bash
git add backend/pune_data.py
git commit -m "feat: add Pune restaurant data with zones and traffic"
```

---

### Task 6: Update Orders Module to Use Real Restaurant Data
**Files:** Modify: `backend/orders.py`

- [ ] **Step 1: Update imports to use pune_data**
```python
# Add after existing imports
try:
    from pune_data import get_all_restaurants, get_zone_center, get_traffic_level
    PUNE_DATA_AVAILABLE = True
except ImportError:
    PUNE_DATA_AVAILABLE = False
```

- [ ] **Step 2: Modify generate_orders to use real restaurants**
```python
# Replace restaurant generation with:
if PUNE_DATA_AVAILABLE and city_name.lower() == "pune":
    restaurants = get_all_restaurants()
    # Generate customer locations within zone with some spread
    # ... use restaurant data
```

- [ ] **Step 3: Test orders with restaurant data**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "
from backend.road_network import load_graph
from backend.orders import generate_orders
G = load_graph('Pune, India')
orders = generate_orders(G, 50, 'Pune, India')
print(f'Generated {len(orders)} orders')
if orders:
    print(f'Sample order: {orders[0].get(\"restaurant_name\")}')
"
```

- [ ] **Step 4: Commit**
```bash
git add backend/orders.py
git commit -m "feat: integrate real Pune restaurant data into orders"
```

---

### Task 7: Update Traffic Module with Time-Based Simulation
**Files:** Modify: `backend/traffic.py`

- [ ] **Step 1: Add time-based traffic simulation**
```python
# Add after imports
try:
    from pune_data import get_time_period, TRAFFIC_ZONES
    PUNE_DATA_AVAILABLE = True
except ImportError:
    PUNE_DATA_AVAILABLE = False

# Add simulation_time parameter to update_traffic
def update_traffic(G, simulation_tick=0, simulation_time_hour=12):
    """Update traffic conditions with time-based simulation."""
    if PUNE_DATA_AVAILABLE:
        period = get_time_period(simulation_time_hour)
        # Apply traffic based on time period
```

- [ ] **Step 2: Run test**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "
from backend.road_network import load_graph
from backend.traffic import update_traffic
G = load_graph('Pune, India')
update_traffic(G, simulation_time_hour=9)  # Morning rush
print('Traffic updated')
"
```

- [ ] **Step 3: Commit**
```bash
git add backend/traffic.py
git commit -m "feat: add time-based traffic simulation"
```

---

### Task 8: Update Simulation Engine with Algorithm Router
**Files:** Modify: `backend/simulation.py:40-50`

- [ ] **Step 1: Import algorithm router**
```python
# Add to imports
try:
    from routing.algorithm_router import select_algorithm, ScenarioParams
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    select_algorithm = None
```

- [ ] **Step 2: Add scenario parameter collection**
```python
# In SimulationEngine, add method to collect scenario params
def _get_scenario_params(self):
    """Collect current scenario parameters for algorithm selection."""
    from routing.algorithm_router import ScenarioParams
    
    # Get current simulation time (convert tick to hour)
    current_hour = 12 + (self.tick_count % 12)  # Simulated hour
    
    # Calculate traffic level
    traffic_data = get_traffic_summary(self.graph)
    avg_traffic = sum(d["avg_multiplier"] for d in traffic_data) / len(traffic_data) if traffic_data else 1.0
    
    pending = sum(1 for o in self.orders[:self.orders_released] if o["status"] == "pending")
    
    return ScenarioParams(
        traffic_density=avg_traffic,
        num_drivers=len(self.drivers),
        num_orders=pending,
        is_urgent=False,  # Could add priority orders
        graph_size=len(self.graph.nodes()),
        is_rush_hour=current_hour in [9, 13, 19, 20]
    )
```

- [ ] **Step 3: Modify _compute_routes to use router**
```python
# In _compute_routes, replace manual algorithm with:
if self.routing_mode == "dynamic" and ROUTER_AVAILABLE:
    params = self._get_scenario_params()
    selected = select_algorithm(params, mode="dynamic")
    current_algorithm = selected.value
else:
    current_algorithm = self.manual_algorithm
```

- [ ] **Step 4: Commit**
```bash
git add backend/simulation.py
git commit -m "feat: integrate algorithm router into simulation engine"
```

---

### Task 9: Add Algorithm Comparison API Endpoint
**Files:** Modify: `backend/main.py:288-306`

- [ ] **Step 1: Enhance algorithm comparison endpoint**
```python
@app.get("/api/algorithms/compare")
async def compare_algorithms(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    """Compare all routing algorithms with detailed metrics."""
    import time
    G = simulation.graph or load_graph()
    source = get_nearest_node(G, from_lat, from_lng)
    target = get_nearest_node(G, to_lat, to_lng)
    
    results = {}
    algorithms = ["dijkstra", "astar", "bfs", "dfs", "greedy"]
    
    for algo in algorithms:
        start = time.time()
        result = find_route(G, source, target, algorithm=algo)
        elapsed = (time.time() - start) * 1000  # ms
        
        results[algo] = {
            "distance_m": result.get("total_distance_m", 0),
            "time_ms": round(elapsed, 2),
            "path_length": len(result.get("path", [])),
            "algorithm": algo
        }
    
    # Floyd-Warshall on small subgraph
    import random
    nodes = list(G.nodes())
    subset = random.sample(nodes, min(100, len(nodes)))
    start = time.time()
    fw_result = floyd_warshall_subgraph(G, subset)
    elapsed = (time.time() - start) * 1000
    
    results["floyd_warshall"] = {
        "distance_m": fw_result.get("shortest_distances", {}).get((source, target), 0),
        "time_ms": round(elapsed, 2),
        "algorithm": "floyd_warshall"
    }
    
    return results
```

- [ ] **Step 2: Test endpoint**
```bash
# Test locally (after starting backend)
curl "http://localhost:8000/api/algorithms/compare?from_lat=18.52&from_lng=73.85&to_lat=18.58&to_lng=73.91"
```

- [ ] **Step 3: Commit**
```bash
git add backend/main.py
git commit -m "feat: add detailed algorithm comparison endpoint"
```

---

### Task 10: Add Heatmap Data API
**Files:** Modify: `backend/main.py`

- [ ] **Step 1: Add heatmap endpoint**
```python
@app.get("/api/heatmap")
async def get_heatmap_data():
    """Get order density heatmap data."""
    if not simulation.orders:
        return {"points": []}
    
    # Aggregate orders by zone
    zone_counts = {}
    from pune_data import PUNE_ZONES
    
    for zone_name in PUNE_ZONES:
        zone_counts[zone_name] = 0
    
    for o in simulation.orders[:simulation.orders_released]:
        if o["status"] != "delivered":
            # Find nearest zone
            for zone_name, zone_data in PUNE_ZONES.items():
                # Simple distance check
                import math
                dist = math.sqrt(
                    (o.get("restaurant_lat", 0) - zone_data["center"][0])**2 +
                    (o.get("restaurant_lng", 0) - zone_data["center"][1])**2
                )
                if dist < 0.05:  # ~5km radius
                    zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1
    
    # Convert to heatmap format
    points = []
    for zone_name, count in zone_counts.items():
        if count > 0:
            center = PUNE_ZONES[zone_name]["center"]
            points.append({
                "lat": center[0],
                "lng": center[1],
                "intensity": count
            })
    
    return {"points": points}
```

- [ ] **Step 2: Commit**
```bash
git add backend/main.py
git commit -m "feat: add heatmap data endpoint"
```

---

### Task 11: Backend Integration Test
**Files:** Test: All backend modules

- [ ] **Step 1: Run full backend integration test**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -c "
# Test all imports
from backend.routing import find_route
from backend.routing.algorithm_router import select_algorithm, ScenarioParams
from backend.routing.genetic_algorithm import genetic_tsp
from backend.pune_data import get_all_restaurants, get_traffic_level
from backend.road_network import load_graph
from backend.orders import generate_orders
from backend.drivers import initialize_drivers
from backend.simulation import SimulationEngine

# Test simulation initialization
sim = SimulationEngine()
sim.initialize(num_orders=100, num_drivers=10, city_name='Pune, India')
print(f'Graph: {len(sim.graph.nodes())} nodes')
print(f'Orders: {len(sim.orders)}')
print(f'Drivers: {len(sim.drivers)}')
print('Backend OK')
"
```

- [ ] **Step 2: Commit**
```bash
git add -A
git commit -m "test: backend integration verification"
```

---

### Task 12: Start Backend Server for Frontend Development
**Files:** N/A - Run backend

- [ ] **Step 1: Start backend server**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -m backend.main
```

- [ ] **Step 2: Verify API endpoints**
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/network/stats
```

---

## Phase 2: Frontend Polish (Tasks 13-22)

### Task 13: Create Premium Dashboard Layout
**Files:** Create: `frontend/src/components/Dashboard.jsx`

- [ ] **Step 1: Create Dashboard component with premium layout**
```jsx
import { useState, useEffect } from 'react';
import MapView from './MapView';
import MetricsPanel from './MetricsPanel';
import AlgorithmSelector from './AlgorithmSelector';
import HeatmapToggle from './HeatmapToggle';
import './Dashboard.css';

function Dashboard({ simState, isConnected, isRunning, config, onUpdateConfig, simSetupConfig, setSimSetupConfig }) {
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`dashboard ${darkMode ? 'dark' : 'light'}`}>
      <header className="dashboard-header">
        <div className="logo-section">
          <span className="logo-icon">🚴</span>
          <h1>DeliveryOS</h1>
          <span className="tag">Pune</span>
        </div>
        
        <div className="controls-section">
          <div className="mode-toggle">
            <button 
              className={config.routing_mode === 'dynamic' ? 'active' : ''}
              onClick={() => onUpdateConfig('dynamic', config.manual_algorithm)}
            >
              🤖 Auto
            </button>
            <button 
              className={config.routing_mode === 'manual' ? 'active' : ''}
              onClick={() => onUpdateConfig('manual', config.manual_algorithm)}
            >
              🎯 Manual
            </button>
          </div>
          
          <label className="heatmap-toggle">
            <input 
              type="checkbox" 
              checked={showHeatmap} 
              onChange={(e) => setShowHeatmap(e.target.checked)} 
            />
            <span>🔥 Heatmap</span>
          </label>
          
          <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        
        <div className="stats-badge">
          <span className={`connection ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● Live' : '○ Offline'}
          </span>
        </div>
      </header>
      
      <main className="dashboard-main">
        <section className="map-section">
          <MapView 
            drivers={simState?.drivers || []}
            orders={simState?.orders || []}
            isRunning={isRunning}
            showHeatmap={showHeatmap}
            city={simSetupConfig.city}
          />
        </section>
        
        <aside className="sidebar">
          <AlgorithmSelector 
            config={config}
            onUpdateConfig={onUpdateConfig}
          />
          <MetricsPanel 
            metrics={simState?.metrics || {}}
            isRunning={isRunning}
          />
        </aside>
      </main>
    </div>
  );
}

export default Dashboard;
```

- [ ] **Step 2: Create Dashboard CSS**
```css
/* frontend/src/components/Dashboard.css */
.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.dashboard.dark {
  --bg-primary: #0a0a0f;
  --bg-secondary: #12121a;
  --bg-tertiary: #1a1a25;
  --accent-primary: #00d4aa;
  --accent-secondary: #6366f1;
  --text-primary: #f0f0f5;
  --text-secondary: #8888a0;
  --border-color: #2a2a3a;
}

.dashboard.light {
  --bg-primary: #f8f9fc;
  --bg-secondary: #ffffff;
  --bg-tertiary: #eef0f5;
  --accent-primary: #0891b2;
  --accent-secondary: #6366f1;
  --text-primary: #1a1a2e;
  --text-secondary: #666680;
  --border-color: #e0e0ea;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-section h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.tag {
  background: var(--accent-primary);
  color: #000;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.controls-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-toggle {
  display: flex;
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
}

.mode-toggle button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.mode-toggle button.active {
  background: var(--accent-primary);
  color: #000;
}

.heatmap-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.theme-toggle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  cursor: pointer;
  font-size: 16px;
}

.stats-badge .connection {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 16px;
}

.connection.connected {
  color: #00d4aa;
  background: rgba(0, 212, 170, 0.1);
}

.connection.disconnected {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.dashboard-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.map-section {
  flex: 1;
  position: relative;
}

.sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
}
```

- [ ] **Step 3: Update App.jsx to use Dashboard**
```jsx
// Replace main App return with:
import Dashboard from './components/Dashboard';

// In App function return:
<Dashboard 
  simState={simState}
  isConnected={isConnected}
  isRunning={isRunning}
  config={simState?.config || { routing_mode: simSetupConfig.routing_mode, manual_algorithm: simSetupConfig.manual_algorithm }}
  onUpdateConfig={updateConfig}
  simSetupConfig={simSetupConfig}
  setSimSetupConfig={setSimSetupConfig}
/>
```

- [ ] **Step 4: Test frontend build**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer\frontend"
npm run build
```

- [ ] **Step 5: Commit**
```bash
git add frontend/src/components/Dashboard.jsx frontend/src/components/Dashboard.css frontend/src/App.jsx
git commit -m "feat: add premium dashboard layout"
```

---

### Task 14: Create Algorithm Selector Cards
**Files:** Create: `frontend/src/components/AlgorithmSelector.jsx`

- [ ] **Step 1: Create AlgorithmSelector component**
```jsx
import './AlgorithmSelector.css';

const algorithms = [
  { id: 'dijkstra', name: 'Dijkstra', icon: '⬡', color: '#00d4aa', desc: 'Optimal for all scenarios' },
  { id: 'astar', name: 'A*', icon: '★', color: '#f59e0b', desc: 'Heuristic best-first' },
  { id: 'bfs', name: 'BFS', icon: '◎', color: '#3b82f6', desc: 'Shortest hops' },
  { id: 'dfs', name: 'DFS', icon: '◇', color: '#8b5cf6', desc: 'Deep exploration' },
  { id: 'greedy', name: 'Greedy', icon: '◆', color: '#ec4899', desc: 'Fast local optimum' },
  { id: 'floyd_warshall', name: 'Floyd', icon: '⬢', color: '#14b8a6', desc: 'All-pairs shortest' },
  { id: 'genetic', name: 'Genetic', icon: '🧬', color: '#f97316', desc: 'Evolutionary optimization' },
];

function AlgorithmSelector({ config, onUpdateConfig }) {
  const isManual = config.routing_mode === 'manual';
  
  return (
    <div className="algorithm-selector">
      <h3>Algorithm</h3>
      {isManual && (
        <div className="algorithm-grid">
          {algorithms.map(algo => (
            <button
              key={algo.id}
              className={`algo-card ${config.manual_algorithm === algo.id ? 'active' : ''}`}
              style={{ '--algo-color': algo.color }}
              onClick={() => onUpdateConfig('manual', algo.id)}
              disabled={!isManual}
            >
              <span className="algo-icon">{algo.icon}</span>
              <span className="algo-name">{algo.name}</span>
              <span className="algo-desc">{algo.desc}</span>
            </button>
          ))}
        </div>
      )}
      {!isManual && (
        <div className="auto-mode-info">
          <span className="auto-icon">🤖</span>
          <p>Dynamic mode active</p>
          <p className="sub">System selects optimal algorithm based on traffic, order density, and urgency</p>
        </div>
      )}
    </div>
  );
}

export default AlgorithmSelector;
```

- [ ] **Step 2: Create AlgorithmSelector CSS**
```css
.algorithm-selector {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: 16px;
}

.algorithm-selector h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.algorithm-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.algo-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border: 2px solid transparent;
  border-radius: 8px;
  background: var(--bg-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.algo-card:hover:not(:disabled) {
  border-color: var(--algo-color);
  transform: translateY(-2px);
}

.algo-card.active {
  border-color: var(--algo-color);
  background: rgba(var(--algo-color), 0.1);
}

.algo-card:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.algo-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.algo-name {
  font-size: 12px;
  font-weight: 600;
}

.algo-desc {
  font-size: 9px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.auto-mode-info {
  text-align: center;
  padding: 20px;
}

.auto-icon {
  font-size: 32px;
}

.auto-mode-info p {
  margin: 8px 0 0;
}

.auto-mode-info .sub {
  font-size: 11px;
  color: var(--text-secondary);
}
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/components/AlgorithmSelector.jsx frontend/src/components/AlgorithmSelector.css
git commit -m "feat: add algorithm selector cards component"
```

---

### Task 15: Enhance Metrics Panel with Animations
**Files:** Modify: `frontend/src/components/MetricsPanel.jsx`

- [ ] **Step 1: Add animated counters**
```jsx
import { useState, useEffect, useRef } from 'react';
import './MetricsPanel.css';

function AnimatedNumber({ value, suffix = '', duration = 500 }) {
  const [displayValue, setDisplayValue] = useState(0);
  const prevValue = useRef(0);
  
  useEffect(() => {
    const start = prevValue.current;
    const end = value;
    const startTime = Date.now();
    
    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      
      setDisplayValue(Math.round(start + (end - start) * eased));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
    prevValue.current = value;
  }, [value, duration]);
  
  return <span>{displayValue}{suffix}</span>;
}

function MetricsPanel({ metrics, isRunning }) {
  const {
    active_drivers = 0,
    total_drivers = 0,
    orders_pending = 0,
    orders_delivered = 0,
    orders_in_transit = 0,
    avg_delivery_time_min = 0,
    total_distance_km = 0,
    utilization_pct = 0,
    tick = 0
  } = metrics;
  
  return (
    <div className="metrics-panel">
      <h3>Live Metrics</h3>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-value">
            <AnimatedNumber value={orders_delivered} />
          </span>
          <span className="metric-label">Delivered</span>
        </div>
        
        <div className="metric-card">
          <span className="metric-value">
            <AnimatedNumber value={orders_in_transit} />
          </span>
          <span className="metric-label">In Transit</span>
        </div>
        
        <div className="metric-card">
          <span className="metric-value">
            <AnimatedNumber value={orders_pending} />
          </span>
          <span className="metric-label">Pending</span>
        </div>
        
        <div className="metric-card highlight">
          <span className="metric-value">
            <AnimatedNumber value={avg_delivery_time_min} suffix="m" />
          </span>
          <span className="metric-label">Avg Time</span>
        </div>
        
        <div className="metric-card">
          <span className="metric-value">
            <AnimatedNumber value={total_distance_km} suffix="km" />
          </span>
          <span className="metric-label">Distance</span>
        </div>
        
        <div className="metric-card">
          <span className="metric-value">
            <AnimatedNumber value={active_drivers} />/
            <AnimatedNumber value={total_drivers} />
          </span>
          <span className="metric-label">Drivers</span>
        </div>
      </div>
      
      <div className="utilization-bar">
        <div className="utilization-label">
          <span>Utilization</span>
          <span><AnimatedNumber value={utilization_pct} suffix="%" /></span>
        </div>
        <div className="bar-track">
          <div 
            className="bar-fill" 
            style={{ width: `${utilization_pct}%` }}
          />
        </div>
      </div>
      
      <div className="tick-info">
        Tick: <AnimatedNumber value={tick} />
      </div>
    </div>
  );
}

export default MetricsPanel;
```

- [ ] **Step 2: Update MetricsPanel CSS with animations**
```css
.metrics-panel {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: 16px;
}

.metrics-panel h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.metric-card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.metric-card.highlight {
  grid-column: span 2;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
}

.metric-card.highlight .metric-value,
.metric-card.highlight .metric-label {
  color: #000;
}

.metric-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.metric-label {
  display: block;
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 4px;
  text-transform: uppercase;
}

.utilization-bar {
  margin-top: 16px;
}

.utilization-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 6px;
}

.bar-track {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 4px;
  transition: width 0.5s ease-out;
}

.tick-info {
  margin-top: 12px;
  text-align: center;
  font-size: 11px;
  color: var(--text-secondary);
}
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/components/MetricsPanel.jsx frontend/src/components/MetricsPanel.css
git commit -m "feat: add animated metrics panel"
```

---

### Task 16: Enhance MapView with Driver Animations
**Files:** Modify: `frontend/src/components/MapView.jsx`

- [ ] **Step 1: Add smooth driver movement**
```jsx
// In MapView component, update driver markers:
const driverIcon = L.divIcon({
  className: 'driver-marker',
  html: `<div class="driver-dot ${driver.status}">
    <span class="driver-icon">🏍</span>
  </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

// Add CSS animation for driver movement
// In MapView.css, add:
.driver-marker {
  transition: transform 0.5s ease-out;
}

.driver-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 212, 170, 0.4);
  animation: pulse 2s infinite;
}

.driver-dot.delivering {
  background: #f59e0b;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
}

.driver-dot.idle {
  background: #6b7280;
  animation: none;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

- [ ] **Step 2: Add route polylines with algorithm colors**
```jsx
// Add route visualization:
useEffect(() => {
  // Clear existing routes
  routeLayers.current.forEach(layer => map.removeLayer(layer));
  routeLayers.current = [];
  
  // Add routes for each driver
  drivers.forEach(driver => {
    if (driver.route_coords && driver.route_coords.length > 1) {
      const routeLine = L.polyline(
        driver.route_coords,
        {
          color: getAlgorithmColor(driver.algorithm || 'dijkstra'),
          weight: 3,
          opacity: 0.7,
          dashArray: driver.status === 'picking' ? '5, 10' : null
        }
      ).addTo(map);
      routeLayers.current.push(routeLine);
    }
  });
}, [drivers]);

const getAlgorithmColor = (algo) => {
  const colors = {
    dijkstra: '#00d4aa',
    astar: '#f59e0b',
    bfs: '#3b82f6',
    dfs: '#8b5cf6',
    greedy: '#ec4899',
    floyd_warshall: '#14b8a6',
    genetic: '#f97316'
  };
  return colors[algo] || '#00d4aa';
};
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/components/MapView.jsx
git commit -m "feat: enhance map with driver animations and routes"
```

---

### Task 17: Add Heatmap Overlay
**Files:** Modify: `frontend/src/components/MapView.jsx`

- [ ] **Step 1: Add heatmap layer**
```jsx
import L from 'leaflet';
import 'leaflet.heat';

// In MapView component:
const [heatmapLayer, setHeatmapLayer] = useState(null);

useEffect(() => {
  if (showHeatmap && orders.length > 0) {
    // Aggregate orders by location
    const heatPoints = orders
      .filter(o => o.status !== 'delivered')
      .map(o => [o.restaurant_lat, o.restaurant_lng, 0.5]);
    
    if (heatmapLayer) {
      map.removeLayer(heatmapLayer);
    }
    
    const heat = L.heatLayer(heatPoints, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: {
        0.2: '#00d4aa',
        0.4: '#f59e0b',
        0.6: '#ef4444',
        0.8: '#dc2626',
        1.0: '#991b1b'
      }
    }).addTo(map);
    
    setHeatmapLayer(heat);
  } else if (heatmapLayer) {
    map.removeLayer(heatmapLayer);
    setHeatmapLayer(null);
  }
}, [showHeatmap, orders]);
```

- [ ] **Step 2: Install heatmap dependency**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer\frontend"
npm install leaflet.heat
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/components/MapView.jsx frontend/package.json
git commit -m "feat: add heatmap overlay to map"
```

---

### Task 18: Add Simulation Controls Panel
**Files:** Create: `frontend/src/components/SimControls.jsx`

- [ ] **Step 1: Create controls component**
```jsx
import './SimControls.css';

function SimControls({ isRunning, onStart, onStop, onReset, config, onConfigChange }) {
  return (
    <div className="sim-controls">
      <h3>Simulation</h3>
      
      <div className="control-buttons">
        {!isRunning ? (
          <button className="btn-start" onClick={onStart}>
            ▶ Start
          </button>
        ) : (
          <button className="btn-stop" onClick={onStop}>
            ⏹ Stop
          </button>
        )}
        <button className="btn-reset" onClick={onReset}>
          ↺ Reset
        </button>
      </div>
      
      <div className="control-sliders">
        <label>
          <span>Drivers</span>
          <input 
            type="range" 
            min="10" 
            max="100" 
            value={config.num_drivers}
            onChange={(e) => onConfigChange({...config, num_drivers: parseInt(e.target.value)})}
          />
          <span className="value">{config.num_drivers}</span>
        </label>
        
        <label>
          <span>Orders</span>
          <input 
            type="range" 
            min="100" 
            max="2000" 
            step="100"
            value={config.num_orders}
            onChange={(e) => onConfigChange({...config, num_orders: parseInt(e.target.value)})}
          />
          <span className="value">{config.num_orders}</span>
        </label>
        
        <label>
          <span>Traffic</span>
          <select 
            value={config.traffic_level}
            onChange={(e) => onConfigChange({...config, traffic_level: e.target.value})}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        
        <label>
          <span>Speed</span>
          <select 
            value={config.vehicle_type}
            onChange={(e) => onConfigChange({...config, vehicle_type: e.target.value})}
          >
            <option value="bike">Bike</option>
            <option value="car">Car</option>
          </select>
        </label>
      </div>
    </div>
  );
}

export default SimControls;
```

- [ ] **Step 2: Create SimControls CSS**
```css
.sim-controls {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: 16px;
}

.sim-controls h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.control-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.control-buttons button {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-start {
  background: #00d4aa;
  color: #000;
}

.btn-stop {
  background: #ef4444;
  color: #fff;
}

.btn-reset {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.control-sliders label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 12px;
}

.control-sliders input[type="range"] {
  flex: 1;
  accent-color: var(--accent-primary);
}

.control-sliders select {
  flex: 1;
  padding: 6px;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.control-sliders .value {
  min-width: 40px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/components/SimControls.jsx frontend/src/components/SimControls.css
git commit -m "feat: add simulation controls panel"
```

---

### Task 19: Create Algorithm Comparison Chart
**Files:** Create: `frontend/src/components/AlgorithmChart.jsx`

- [ ] **Step 1: Create chart component**
```jsx
import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './AlgorithmChart.css';

function AlgorithmChart({ comparisonData, isLoading }) {
  if (isLoading) {
    return <div className="algo-chart loading">Loading comparison...</div>;
  }
  
  if (!comparisonData || Object.keys(comparisonData).length === 0) {
    return <div className="algo-chart empty">Run comparison to see metrics</div>;
  }
  
  const chartData = Object.entries(comparisonData).map(([algo, data]) => ({
    name: algo,
    distance: data.distance_m || 0,
    time: data.time_ms || 0,
    pathLength: data.path_length || 0
  }));
  
  return (
    <div className="algo-chart">
      <h3>Algorithm Comparison</h3>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={chartData} layout="vertical">
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" width={80} tick={{fontSize: 10}} />
            <Tooltip 
              contentStyle={{ 
                background: '#1a1a25', 
                border: 'none',
                borderRadius: 8 
              }}
            />
            <Bar dataKey="time" fill="#00d4aa" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="chart-legend">
        <span>⏱ Execution time (ms)</span>
      </div>
    </div>
  );
}

export default AlgorithmChart;
```

- [ ] **Step 2: Create chart CSS**
```css
.algo-chart {
  background: var(--bg-tertiary);
  border-radius: 12px;
  padding: 16px;
}

.algo-chart h3 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.chart-container {
  margin: 0 -8px;
}

.chart-legend {
  text-align: center;
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.algo-chart.loading,
.algo-chart.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  color: var(--text-secondary);
  font-size: 13px;
}
```

- [ ] **Step 3: Install recharts**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer\frontend"
npm install recharts
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/components/AlgorithmChart.jsx frontend/src/components/AlgorithmChart.css frontend/package.json
git commit -m "feat: add algorithm comparison chart"
```

---

### Task 20: Final Frontend Integration
**Files:** Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Update App with all components**
```jsx
import { useState, useEffect, useRef, useCallback } from 'react';
import Dashboard from './components/Dashboard';
import SimControls from './components/SimControls';
import AlgorithmChart from './components/AlgorithmChart';
import './App.css';

function App() {
  // ... existing state ...
  
  const [debugRouteData, setDebugRouteData] = useState(null);
  const [debugLoading, setDebugLoading] = useState(false);
  
  const fetchDebugRoute = async () => {
    // ... existing implementation ...
  };
  
  const handleConfigChange = (newConfig) => {
    setSimSetupConfig(newConfig);
  };
  
  return (
    <Dashboard
      simState={simState}
      isConnected={isConnected}
      isRunning={isRunning}
      config={simState?.config || { routing_mode: simSetupConfig.routing_mode, manual_algorithm: simSetupConfig.manual_algorithm }}
      onUpdateConfig={updateConfig}
      simSetupConfig={simSetupConfig}
      setSimSetupConfig={setSimSetupConfig}
    >
      <SimControls
        isRunning={isRunning}
        onStart={startSimulation}
        onStop={stopSimulation}
        onReset={resetSimulation}
        config={simSetupConfig}
        onConfigChange={handleConfigChange}
      />
      <AlgorithmChart 
        comparisonData={debugRouteData}
        isLoading={debugLoading}
      />
    </Dashboard>
  );
}

export default App;
```

- [ ] **Step 2: Test full frontend**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer\frontend"
npm run build
```

- [ ] **Step 3: Commit**
```bash
git add frontend/src/App.jsx
git commit -m "feat: final frontend integration"
```

---

## Phase 3: Portfolio Documentation (Tasks 21-22)

### Task 21: Create Comprehensive README
**Files:** Create: `README.md`

- [ ] **Step 1: Create portfolio README with architecture diagram**
```markdown
# 🍔 Food Delivery Route Optimizer

A real-time food delivery routing simulation platform built with FastAPI and React. Demonstrates intelligent algorithm selection, live dispatch simulation, and portfolio-grade visualization.

## 🚀 Features

- **6 Routing Algorithms**: Dijkstra, A*, BFS, DFS, Greedy Best-First, Floyd-Warshall
- **Dynamic Algorithm Selection**: System automatically picks optimal algorithm based on:
  - Traffic density
  - Order volume
  - Delivery urgency
  - Time of day
- **Real-time Simulation**: Live drivers, orders, routes on Pune map
- **Algorithm Comparison**: Side-by-side performance metrics
- **Heatmap Visualization**: Demand zone overlay
- **Premium Dashboard**: Dark/light theme, smooth animations

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  Dashboard │ MapView │ MetricsPanel │ AlgorithmSelector    │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket + REST
┌──────────────────────────▼──────────────────────────────────┐
│                       Backend (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  SimulationEngine                                           │
│  ├── Route Optimizer (TSP/VRP)                              │
│  ├── Algorithm Router (Dynamic Selection)                   │
│  ├── Batching Engine (Multi-order)                          │
│  └── Traffic Simulator                                      │
├─────────────────────────────────────────────────────────────┤
│  Routing Module                                              │
│  ├── Dijkstra │ A* │ BFS │ DFS │ Greedy │ Floyd-Warshall   │
│  └── Genetic Algorithm (TSP)                                │
├─────────────────────────────────────────────────────────────┤
│  Data Modules                                                │
│  ├── Pune Restaurant Data (7 zones, 100+ restaurants)       │
│  ├── Road Network Graph                                      │
│  └── Time-based Traffic Simulation                          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Algorithm Complexity

| Algorithm | Time Complexity | Space Complexity | Best For |
|-----------|-----------------|------------------|----------|
| Dijkstra | O((V+E)logV) | O(V) | General shortest path |
| A* | O(E) | O(V) | Heuristic-guided search |
| BFS | O(V+E) | O(V) | Unweighted shortest path |
| DFS | O(V+E) | O(V) | Path exploration |
| Greedy | O(E log E) | O(V) | Fast local optimum |
| Floyd-Warshall | O(V³) | O(V²) | All-pairs shortest path |
| Genetic | O(G × P × N²) | O(P × N) | Large-scale TSP |

## 🛠 Setup

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m backend.main

# Frontend
cd frontend
npm install
npm run dev
```

## 🎯 Usage

1. Start backend server (runs on http://localhost:8000)
2. Start frontend (runs on http://localhost:5173)
3. Configure simulation: drivers, orders, traffic level
4. Choose mode: Auto (dynamic) or Manual (select algorithm)
5. Start simulation and watch real-time dispatch

## 📁 Project Structure

```
food-delivery-optimizer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── simulation.py        # Core simulation engine
│   ├── routing.py           # Pathfinding algorithms
│   ├── route_optimizer.py   # TSP/VRP optimization
│   ├── pune_data.py         # Restaurant & zone data
│   ├── traffic.py           # Traffic simulation
│   ├── orders.py            # Order generation
│   ├── drivers.py           # Driver management
│   └── batching.py          # Order batching
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx          # Main application
│   │   └── App.css          # Global styles
│   └── package.json
├── docs/                    # Design specs & plans
└── README.md
```

## 🎓 Academic Context

This project demonstrates:
- Graph algorithms and pathfinding
- Real-time systems and WebSocket communication
- Algorithm selection based on scenario parameters
- TSP/VRP approximations
- Modern React frontend development

## 📸 Screenshots

[Add screenshots here]

## 📝 License

MIT
```

- [ ] **Step 2: Commit**
```bash
git add README.md
git commit -m "docs: add comprehensive README with architecture"
```

---

### Task 22: Final Testing & Demo Preparation
**Files:** Test all integrations

- [ ] **Step 1: Run full system test**
```bash
# Start backend
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer"
python -m backend.main &

# Start frontend
cd frontend
npm run dev

# Test API endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/network/stats
curl http://localhost:8000/api/heatmap
```

- [ ] **Step 2: Run browser test with Playwright**
```bash
cd "D:\Vit\Academics Sem-4\ADSA\CP\food-delivery-optimizer\frontend"
npx playwright test
```

- [ ] **Step 3: Final commit**
```bash
git add -A
git commit -m "feat: complete food delivery optimizer v1.0"
```

---

## Execution Summary

**Total Tasks: 22**

- **Phase 1 (Backend Core)**: Tasks 1-12
- **Phase 2 (Frontend Polish)**: Tasks 13-20
- **Phase 3 (Documentation)**: Tasks 21-22

**Key Dependencies:**
- Backend: FastAPI, NetworkX, NumPy
- Frontend: React 18, Vite, Leaflet, Recharts

**Expected Completion:**
- Polished version: 5-7 days
- Strong final version: 10-14 days