"""
Route Optimization
Greedy TSP approximation for multi-stop delivery routes.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
from routing import find_route as _find_route, haversine as _haversine
find_route = _find_route
haversine = _haversine
from road_network import get_nearest_node, get_node_coords

import sys
import os
try:
    from routing_algorithms.algorithm_router import select_algorithm, AlgorithmType
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    AlgorithmType = None


def _build_distance_matrix(G, stop_nodes, routing_mode="dynamic", manual_algorithm="dijkstra", traffic_level=1.0, is_urgent=False):
    """Build a distance matrix between all stops using shortest paths."""
    n = len(stop_nodes)
    dist_matrix = [[0] * n for _ in range(n)]
    path_cache = {}

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            result = find_route(G, stop_nodes[i], stop_nodes[j], algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level, is_urgent=is_urgent)
            if "error" not in result:
                dist_matrix[i][j] = result["total_distance_m"]
                path_cache[(i, j)] = result["path_coords"]
            else:
                # Fallback: haversine estimate
                ci = get_node_coords(G, stop_nodes[i])
                cj = get_node_coords(G, stop_nodes[j])
                dist_matrix[i][j] = haversine(ci[0], ci[1], cj[0], cj[1])
                path_cache[(i, j)] = [ci, cj]

    return dist_matrix, path_cache


def greedy_tsp(G, stop_nodes, start_node=None, routing_mode="dynamic", manual_algorithm="dijkstra", traffic_level=1.0, is_urgent=False):
    """
    Greedy nearest-neighbor TSP approximation.

    Args:
        G: road network graph
        stop_nodes: list of graph nodes to visit
        start_node: starting node (if None, uses first stop)

    Returns:
        optimized_order: indices into stop_nodes
        full_route_coords: complete lat/lng path
        total_distance: total route distance in meters
    """
    if len(stop_nodes) <= 1:
        coords = [get_node_coords(G, n) for n in stop_nodes]
        return list(range(len(stop_nodes))), coords, 0

    # Include start node if provided
    all_nodes = list(stop_nodes)
    if start_node is not None and start_node not in all_nodes:
        all_nodes = [start_node] + all_nodes

    dist_matrix, path_cache = _build_distance_matrix(G, all_nodes, routing_mode, manual_algorithm, traffic_level, is_urgent)

    n = len(all_nodes)
    visited = [False] * n
    order = [0]  # Start from first node (or start_node)
    visited[0] = True

    for _ in range(n - 1):
        current = order[-1]
        best_next = -1
        best_dist = float("inf")

        for j in range(n):
            if not visited[j] and dist_matrix[current][j] < best_dist:
                best_dist = dist_matrix[current][j]
                best_next = j

        if best_next == -1:
            break

        order.append(best_next)
        visited[best_next] = True

    # Build full route coordinates
    full_route_coords = []
    total_distance = 0

    for i in range(len(order) - 1):
        from_idx = order[i]
        to_idx = order[i + 1]
        total_distance += dist_matrix[from_idx][to_idx]

        path = path_cache.get((from_idx, to_idx), [])
        if full_route_coords and path:
            path = path[1:]  # Skip duplicate starting point
        full_route_coords.extend(path)

    # If start_node was added, adjust order to be relative to original stop_nodes
    if start_node is not None and start_node not in stop_nodes:
        order = [i - 1 for i in order if i > 0]

    return order, full_route_coords, total_distance


def optimize_driver_route(G, driver, orders_list, routing_mode="dynamic", manual_algorithm="dijkstra", traffic_level=1.0):
    """
    Optimize a driver's delivery route.

    Args:
        G: road network graph
        driver: driver dict
        orders_list: list of order dicts assigned to this driver

    Returns:
        route_coords: full lat/lng route
        stop_sequence: ordered list of stops
        total_distance: total distance in meters
    """
    if not orders_list:
        return [], [], 0

    is_urgent = any(order.get("is_priority", False) for order in orders_list)

    # Build stop list: restaurant pickups then customer deliveries
    pickup_nodes = []
    delivery_nodes = []

    for order in orders_list:
        pickup_nodes.append(order["restaurant_node"])
        delivery_nodes.append(order["customer_node"])

    # Strategy: visit all restaurants first, then deliver to customers
    # Optimize within each phase
    driver_node = driver.get("current_node")

    # Optimize restaurant visit order
    if len(pickup_nodes) > 1:
        pickup_order, pickup_coords, pickup_dist = greedy_tsp(G, pickup_nodes, start_node=driver_node, routing_mode=routing_mode, manual_algorithm=manual_algorithm, traffic_level=traffic_level, is_urgent=is_urgent)
        ordered_pickups = [pickup_nodes[i] for i in pickup_order]
    else:
        ordered_pickups = pickup_nodes
        pickup_coords = []
        pickup_dist = 0

    # Optimize delivery order
    if len(delivery_nodes) > 1:
        last_pickup = ordered_pickups[-1] if ordered_pickups else driver_node
        delivery_order, delivery_coords, delivery_dist = greedy_tsp(G, delivery_nodes, start_node=last_pickup, routing_mode=routing_mode, manual_algorithm=manual_algorithm, traffic_level=traffic_level, is_urgent=is_urgent)
        ordered_deliveries = [delivery_nodes[i] for i in delivery_order]
    else:
        ordered_deliveries = delivery_nodes
        delivery_coords = []
        delivery_dist = 0

    # Build complete route: driver → restaurants → customers
    all_stops = []
    full_route = []
    total_dist = 0

    # Driver to first restaurant
    if driver_node and ordered_pickups:
        result = find_route(G, driver_node, ordered_pickups[0], algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level, is_urgent=is_urgent)
        if "error" not in result:
            full_route.extend(result["path_coords"])
            total_dist += result["total_distance_m"]
        all_stops.append({"type": "pickup", "node": ordered_pickups[0], "coords": get_node_coords(G, ordered_pickups[0])})

    # Between restaurants
    for i in range(len(ordered_pickups) - 1):
        result = find_route(G, ordered_pickups[i], ordered_pickups[i + 1], algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level, is_urgent=is_urgent)
        if "error" not in result:
            coords = result["path_coords"][1:]  # skip duplicate
            full_route.extend(coords)
            total_dist += result["total_distance_m"]
        all_stops.append({"type": "pickup", "node": ordered_pickups[i + 1], "coords": get_node_coords(G, ordered_pickups[i + 1])})

    # Last restaurant to first customer
    if ordered_pickups and ordered_deliveries:
        result = find_route(G, ordered_pickups[-1], ordered_deliveries[0], algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level, is_urgent=is_urgent)
        if "error" not in result:
            coords = result["path_coords"][1:]
            full_route.extend(coords)
            total_dist += result["total_distance_m"]
        all_stops.append({"type": "delivery", "node": ordered_deliveries[0], "coords": get_node_coords(G, ordered_deliveries[0])})

    # Between customers
    for i in range(len(ordered_deliveries) - 1):
        result = find_route(G, ordered_deliveries[i], ordered_deliveries[i + 1], algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level, is_urgent=is_urgent)
        if "error" not in result:
            coords = result["path_coords"][1:]
            full_route.extend(coords)
            total_dist += result["total_distance_m"]
        all_stops.append({"type": "delivery", "node": ordered_deliveries[i + 1], "coords": get_node_coords(G, ordered_deliveries[i + 1])})

    return full_route, all_stops, total_dist
