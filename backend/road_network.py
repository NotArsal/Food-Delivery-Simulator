"""
Road Network Engine
Downloads and manages Pune's road network using OSMnx and NetworkX.
"""
import os
import math
import time
import networkx as nx

try:
    import osmnx as ox
except ImportError:
    ox = None

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
GRAPH_FILE = os.path.join(DATA_DIR, "pune_graph.graphml")

# Pune bounding box
PUNE_CENTER = (18.5204, 73.8567)
PUNE_BOUNDS = {
    "north": 18.60,
    "south": 18.45,
    "east": 73.95,
    "west": 73.75,
}

_graph = None


def _configure_osmnx():
    """Configure OSMnx for faster, cached downloads."""
    if ox is None:
        return
    ox.settings.use_cache = True
    ox.settings.cache_folder = os.path.join(DATA_DIR, "cache")
    ox.settings.timeout = 180


def _add_base_attributes(G):
    """Add base travel time and traffic multiplier to all edges."""
    for u, v, data in G.edges(data=True):
        length = data.get("length", 100)  # meters
        # Assume average speed 30 km/h = 8.33 m/s in city
        base_speed = 8.33  # m/s
        data["base_travel_time"] = length / base_speed
        data["travel_time"] = data["base_travel_time"]
        data["traffic_multiplier"] = 1.0
        data["distance"] = length
    return G


def download_graph(city_name="Pune, India"):
    """Download road network from OpenStreetMap around the city center."""
    if ox is None:
        raise ImportError("osmnx is required. Install with: pip install osmnx")

    _configure_osmnx()

    print(f"Downloading {city_name} road network from OpenStreetMap (4km radius)...")
    try:
        lat, lng = ox.geocode(city_name)
    except Exception as e:
        print(f"Failed to geocode {city_name}, falling back to Pune center.")
        lat, lng = PUNE_CENTER

    try:
        merged_graph = ox.graph_from_point(
            (lat, lng),
            dist=4000,
            network_type="drive",
            simplify=True,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to download graph for {city_name}: {e}")

    # 3x3 grid → 9 chunks (reduced from 5x5)
    grid_rows = 3
    grid_cols = 3
    lat_step = (PUNE_BOUNDS["north"] - PUNE_BOUNDS["south"]) / grid_rows
    G = _add_base_attributes(merged_graph)

    os.makedirs(DATA_DIR, exist_ok=True)
    ox.save_graphml(G, GRAPH_FILE)
    print(f"\nGraph saved to {GRAPH_FILE}")
    print(f"Total Nodes: {G.number_of_nodes()}, Total Edges: {G.number_of_edges()}")

    return G


def _create_synthetic_graph():
    """Create a synthetic grid-like road network for Pune when OSMnx is unavailable."""
    print("Creating synthetic Pune road network (OSMnx not available)...")

    G = nx.DiGraph()

    lat_min, lat_max = PUNE_BOUNDS["south"], PUNE_BOUNDS["north"]
    lng_min, lng_max = PUNE_BOUNDS["west"], PUNE_BOUNDS["east"]

    grid_size = 50  # 50x50 grid = 2500 nodes
    lat_step = (lat_max - lat_min) / (grid_size - 1)
    lng_step = (lng_max - lng_min) / (grid_size - 1)

    node_id = 0
    node_grid = {}

    for i in range(grid_size):
        for j in range(grid_size):
            lat = lat_min + i * lat_step
            lng = lng_min + j * lng_step
            G.add_node(node_id, y=lat, x=lng)
            node_grid[(i, j)] = node_id
            node_id += 1

    def haversine_dist(lat1, lng1, lat2, lng2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    for i in range(grid_size):
        for j in range(grid_size):
            current = node_grid[(i, j)]
            current_data = G.nodes[current]

            neighbors = []
            if i + 1 < grid_size:
                neighbors.append((i + 1, j))
            if j + 1 < grid_size:
                neighbors.append((i, j + 1))
            if i - 1 >= 0:
                neighbors.append((i - 1, j))
            if j - 1 >= 0:
                neighbors.append((i, j - 1))

            for ni, nj in neighbors:
                neighbor = node_grid[(ni, nj)]
                neighbor_data = G.nodes[neighbor]
                dist = haversine_dist(
                    current_data["y"], current_data["x"],
                    neighbor_data["y"], neighbor_data["x"]
                )
                base_speed = 8.33
                base_time = dist / base_speed

                G.add_edge(current, neighbor,
                           length=dist,
                           distance=dist,
                           base_travel_time=base_time,
                           travel_time=base_time,
                           traffic_multiplier=1.0)

    print(f"Synthetic graph: Nodes={G.number_of_nodes()}, Edges={G.number_of_edges()}")
    return G


def load_graph(city_name="Pune, India"):
    """Load the road network graph, downloading if necessary."""
    global _graph

    clean_name = city_name.replace(", ", "_").replace(" ", "_").lower()
    graph_file = os.path.join(DATA_DIR, f"{clean_name}_graph.graphml")

    if _graph is not None and getattr(_graph, "city_name", "") == city_name:
        return _graph

    if os.path.exists(graph_file) and ox is not None:
        print(f"Loading cached graph from {graph_file}...")
        _graph = ox.load_graphml(graph_file)
        _graph = _add_base_attributes(_graph)
    elif ox is not None:
        try:
            _graph = download_graph(city_name)
            os.makedirs(DATA_DIR, exist_ok=True)
            ox.save_graphml(_graph, graph_file)
        except Exception as e:
            print(f"Failed to download graph: {e}")
            print("Falling back to synthetic graph...")
            _graph = _create_synthetic_graph()
    else:
        _graph = _create_synthetic_graph()

    _graph.city_name = city_name
    return _graph


def get_nearest_node(G, lat, lng):
    """Find the nearest graph node to given coordinates."""
    if ox is not None:
        try:
            return ox.nearest_nodes(G, lng, lat)
        except Exception:
            pass

    # Manual fallback
    min_dist = float("inf")
    nearest = None
    for node, data in G.nodes(data=True):
        node_lat = data.get("y", 0)
        node_lng = data.get("x", 0)
        dist = math.sqrt((node_lat - lat) ** 2 + (node_lng - lng) ** 2)
        if dist < min_dist:
            min_dist = dist
            nearest = node
    return nearest


def get_node_coords(G, node):
    """Get (lat, lng) coordinates of a node."""
    data = G.nodes[node]
    return (data.get("y", 0), data.get("x", 0))


def get_graph_stats(G):
    """Return basic graph statistics."""
    return {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "center": PUNE_CENTER,
        "bounds": PUNE_BOUNDS,
    }
