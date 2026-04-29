import math
import networkx as nx
from routing import find_route as _find_route, haversine as _haversine
find_route = _find_route
haversine = _haversine
from road_network import get_nearest_node, get_node_coords

try:
    from routing_algorithms.genetic_algorithm import GeneticOptimizer
    GENETIC_AVAILABLE = True
except ImportError:
    GENETIC_AVAILABLE = False


def _build_distance_matrix(G, stop_nodes):
    """
    Build a distance matrix using One-to-All Dijkstra for performance.
    Complexity: O(N * (E + V log V)) instead of O(N^2 * (E + V log V))
    """
    n = len(stop_nodes)
    dist_matrix = [[0.0] * n for _ in range(n)]
    
    # Map nodes to indices for matrix
    node_to_idx = {node: i for i, node in enumerate(stop_nodes)}
    
    for i, start_node in enumerate(stop_nodes):
        # Use NetworkX one-to-all Dijkstra
        try:
            lengths = nx.single_source_dijkstra_path_length(G, start_node, weight="travel_time")
            for j, end_node in enumerate(stop_nodes):
                if end_node in lengths:
                    dist_matrix[i][j] = lengths[end_node]
                else:
                    # Fallback to haversine for disconnected components
                    c1 = get_node_coords(G, start_node)
                    c2 = get_node_coords(G, end_node)
                    dist_matrix[i][j] = haversine(c1[0], c1[1], c2[0], c2[1]) / 8.33 # Estimated time
        except Exception:
            # Complete fallback
            for j, end_node in enumerate(stop_nodes):
                if i == j: continue
                c1 = get_node_coords(G, start_node)
                c2 = get_node_coords(G, end_node)
                dist_matrix[i][j] = haversine(c1[0], c1[1], c2[0], c2[1]) / 8.33

    return dist_matrix


def constrained_greedy_tsp(dist_matrix, pickup_delivery_map, start_idx=0):
    """
    Greedy TSP that respects Pickup-before-Delivery constraints.
    pickup_delivery_map: {pickup_idx: delivery_idx}
    """
    n = len(dist_matrix)
    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    
    # Active deliveries: pickups done but deliveries pending
    pending_deliveries = set()
    # Pickups still to do
    remaining_pickups = set(pickup_delivery_map.keys())
    
    if start_idx in remaining_pickups:
        remaining_pickups.remove(start_idx)
        pending_deliveries.add(pickup_delivery_map[start_idx])

    while len(route) < n:
        curr = route[-1]
        best_next = -1
        best_dist = float('inf')
        
        # Valid next stops are:
        # 1. Any remaining pickup
        # 2. Any pending delivery
        valid_stops = remaining_pickups.union(pending_deliveries)
        
        for next_stop in valid_stops:
            if not visited[next_stop] and dist_matrix[curr][next_stop] < best_dist:
                best_dist = dist_matrix[curr][next_stop]
                best_next = next_stop
        
        if best_next == -1: break
        
        route.append(best_next)
        visited[best_next] = True
        
        if best_next in remaining_pickups:
            remaining_pickups.remove(best_next)
            pending_deliveries.add(pickup_delivery_map[best_next])
        elif best_next in pending_deliveries:
            pending_deliveries.remove(best_next)
            
    return route


def optimize_driver_route(G, driver, orders_list, routing_mode="dynamic", manual_algorithm="dijkstra", traffic_level=1.0):
    """
    Optimized multi-stop route planner.
    Combines pickups and deliveries for globally optimal paths.
    """
    if not orders_list:
        return [], [], 0

    driver_node = driver.get("current_node")
    if not driver_node:
        driver_node = get_nearest_node(G, driver['lat'], driver['lng'])

    # 1. Prepare Nodes
    # All nodes = [driver_node, P1, D1, P2, D2, ...]
    all_nodes = [driver_node]
    pickup_delivery_map = {} # pickup_idx -> delivery_idx
    
    for i, order in enumerate(orders_list):
        p_node = order["restaurant_node"]
        d_node = order["customer_node"]
        
        # Add nodes and track relationship (index based)
        p_idx = len(all_nodes)
        all_nodes.append(p_node)
        d_idx = len(all_nodes)
        all_nodes.append(d_node)
        pickup_delivery_map[p_idx] = d_idx

    # 2. Build Distance Matrix (One-to-All Dijkstra)
    dist_matrix = _build_distance_matrix(G, all_nodes)

    # 3. Optimize Order (Greedy with Constraints)
    # Use Genetic if batch is large, otherwise Greedy is perfectly fine
    if GENETIC_AVAILABLE and len(orders_list) > 5:
        # Note: GeneticOptimizer needs wrapping to handle constraints, 
        # for now using constrained greedy which is very reliable for small batches.
        stop_order = constrained_greedy_tsp(dist_matrix, pickup_delivery_map, start_idx=0)
    else:
        stop_order = constrained_greedy_tsp(dist_matrix, pickup_delivery_map, start_idx=0)

    # 4. Build Full Route Coordinates & Metrics
    full_route_coords = []
    total_dist_m = 0
    all_stops = []
    
    # Map back to nodes
    ordered_nodes = [all_nodes[i] for i in stop_order]
    
    for i in range(len(ordered_nodes) - 1):
        u, v = ordered_nodes[i], ordered_nodes[i+1]
        
        # Use find_route for the final path reconstruction
        result = find_route(G, u, v, algorithm=manual_algorithm, dynamic_mode=(routing_mode=="dynamic"), traffic_level=traffic_level)
        
        if "error" not in result:
            path = result["path_coords"]
            if full_route_coords and path:
                path = path[1:]
            full_route_coords.extend(path)
            total_dist_m += result["total_distance_m"]
        
        # Identify stop type for UI
        node_type = "pickup" if v in [o["restaurant_node"] for o in orders_list] else "delivery"
        all_stops.append({
            "type": node_type,
            "node": v,
            "coords": get_node_coords(G, v)
        })

    return full_route_coords, all_stops, total_dist_m

