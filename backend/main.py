"""
Food Delivery Route Optimizer - FastAPI Backend
Main application with REST endpoints and WebSocket server.
"""
import os
import sys
import json
import asyncio
import time
from typing import Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Add parent dir to path for ML imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ml_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml")
sys.path.insert(0, ml_dir)

from road_network import load_graph, get_graph_stats, get_nearest_node
from routing import find_route, floyd_warshall_subgraph
from traffic import get_traffic_summary, update_traffic
from orders import get_order_stats
from drivers import get_driver_stats
from simulation import SimulationEngine
from pydantic import BaseModel

# Try to import ML predictor
try:
    from predict import predict_eta, load_model
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False

# Global state
simulation: SimulationEngine = SimulationEngine()
ws_clients: Set[WebSocket] = set()
sim_task = None


@asynccontextmanager
async def lifespan(app):
    """Pre-load graph on startup."""
    print("[APP] Starting Food Delivery Route Optimizer...")
    simulation.initialize()
    print("[APP] Ready! API docs at http://localhost:8000/docs")
    yield
    simulation.stop()
    print("[APP] Shutting down.")


app = FastAPI(
    title="Food Delivery Route Optimizer",
    description="Logistics simulation platform for Pune, India",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - note: allow_credentials=True is incompatible with allow_origins=["*"] per CORS spec
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def broadcast_state(state):
    """Broadcast simulation state to all WebSocket clients."""
    if not ws_clients:
        return
    message = json.dumps(state, default=str)
    disconnected = []
    for ws in ws_clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        ws_clients.discard(ws)
    for ws in disconnected:
        ws_clients.discard(ws)


# ─── REST ENDPOINTS ─────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "name": "Food Delivery Route Optimizer",
        "version": "1.0.0",
        "status": "running",
        "ml_available": ML_AVAILABLE,
    }


@app.get("/api/network/stats")
async def network_stats():
    """Get road network statistics."""
    G = simulation.graph or load_graph()
    stats = get_graph_stats(G)
    traffic = get_traffic_summary(G)
    return {"graph": stats, "traffic": traffic}


@app.get("/api/orders")
async def get_orders():
    """Get current orders and statistics."""
    if not simulation.orders:
        return {"orders": [], "stats": {"total_orders": 0}}
    stats = get_order_stats(simulation.orders[:simulation.orders_released])
    # Return limited orders for performance
    visible = []
    for o in simulation.orders[:simulation.orders_released]:
        visible.append({
            "order_id": o["order_id"],
            "restaurant_lat": o["restaurant_lat"],
            "restaurant_lng": o["restaurant_lng"],
            "customer_lat": o["customer_lat"],
            "customer_lng": o["customer_lng"],
            "restaurant_name": o.get("restaurant_name", "Unknown"),
            "restaurant_zone": o.get("restaurant_zone", "Unknown"),
            "status": o["status"],
        })
    return {"orders": visible[:200], "stats": stats}


@app.get("/api/drivers")
async def get_drivers():
    """Get driver states."""
    if not simulation.drivers:
        return {"drivers": [], "stats": {"total_drivers": 0}}
    stats = get_driver_stats(simulation.drivers)
    driver_list = []
    for d in simulation.drivers:
        driver_list.append({
            "driver_id": d["driver_id"],
            "lat": d["lat"],
            "lng": d["lng"],
            "status": d["status"],
            "deliveries": d["stats"]["deliveries_completed"],
            "active_batch": d["active_batch"],
        })
    return {"drivers": driver_list, "stats": stats}


@app.get("/api/metrics")
async def get_metrics():
    """Get simulation metrics."""
    return simulation.metrics


class SimStartConfig(BaseModel):
    num_orders: int = 1000
    num_drivers: int = 50
    city: str = "Pune, India"
    tick_delay: float = 2.0


@app.post("/api/simulation/start")
async def start_simulation(config: SimStartConfig = None):
    """Start the city-scale simulation."""
    global sim_task

    if simulation.is_running:
        return {"status": "already_running"}

    # Initialize if needed
    if config:
        # Re-initialize with new config if provided
        try:
            simulation.initialize(num_orders=config.num_orders, num_drivers=config.num_drivers, city_name=config.city)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    elif not simulation.graph:
        simulation.initialize()

    # Start simulation in background
    sim_task = asyncio.create_task(simulation.run(ws_broadcast_callback=broadcast_state))

    return {
        "status": "started",
        "total_orders": len(simulation.orders),
        "total_drivers": len(simulation.drivers),
    }


@app.post("/api/simulation/stop")
async def stop_simulation():
    """Stop the simulation."""
    simulation.stop()
    return {"status": "stopped", "metrics": simulation.metrics}


@app.post("/api/simulation/reset")
async def reset_simulation(config: SimStartConfig = None):
    """Reset the simulation."""
    simulation.stop()
    global sim_task
    if sim_task:
        sim_task.cancel()
        sim_task = None
    if config:
        simulation.initialize(num_orders=config.num_orders, num_drivers=config.num_drivers, city_name=config.city)
    else:
        simulation.initialize()
    return {"status": "reset"}


@app.post("/api/simulation/config")
async def update_config(data: dict):
    """Update simulation routing configuration."""
    if "routing_mode" in data:
        simulation.routing_mode = data["routing_mode"]
    if "manual_algorithm" in data:
        simulation.manual_algorithm = data["manual_algorithm"]
    return {
        "status": "success", 
        "config": {
            "routing_mode": simulation.routing_mode, 
            "manual_algorithm": simulation.manual_algorithm
        }
    }


@app.post("/api/predict-eta")
async def predict_delivery_eta(data: dict):
    """Predict delivery time using ML model."""
    if not ML_AVAILABLE:
        # Fallback: simple calculation
        distance = data.get("distance", 5000)
        traffic = data.get("traffic_level", 1.0)
        stops = data.get("num_stops", 1)
        hour = data.get("hour", 12)

        # Simple estimate: 30 km/h base speed + traffic + stop overhead
        base_time_min = (distance / 1000) / 30 * 60
        traffic_factor = traffic
        stop_overhead = stops * 3  # 3 min per stop
        eta = base_time_min * traffic_factor + stop_overhead

        return {
            "predicted_eta_minutes": round(eta, 1),
            "model": "fallback_calculation",
            "confidence": 0.6,
        }

    try:
        eta = predict_eta(
            distance=data.get("distance", 5000),
            traffic_level=data.get("traffic_level", 1.0),
            num_stops=data.get("num_stops", 1),
            hour=data.get("hour", 12),
        )
        return {
            "predicted_eta_minutes": round(eta, 1),
            "model": "random_forest",
            "confidence": 0.85,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/route")
async def compute_route(
    from_lat: float, from_lng: float,
    to_lat: float, to_lng: float,
    algorithm: str = "dijkstra",
    routing_mode: str = "manual"
):
    """Compute a route between two points."""
    G = simulation.graph or load_graph()
    source = get_nearest_node(G, from_lat, from_lng)
    target = get_nearest_node(G, to_lat, to_lng)

    # get_traffic_summary returns a dict with keys: low, medium, high, total_edges, etc.
    traffic_data = get_traffic_summary(G)
    total_edges = traffic_data.get("total_edges", 0)
    if total_edges > 0:
        avg_traffic = (
            traffic_data.get("low", 0) * 1.0
            + traffic_data.get("medium", 0) * 1.3
            + traffic_data.get("high", 0) * 1.8
        ) / total_edges
    else:
        avg_traffic = 1.0

    result = find_route(
        G, source, target,
        algorithm=algorithm,
        dynamic_mode=(routing_mode == "dynamic"),
        traffic_level=avg_traffic
    )
    return result


@app.get("/api/algorithms/compare")
async def compare_algorithms(from_lat: float, from_lng: float, to_lat: float, to_lng: float):
    """Compare all routing algorithms with detailed metrics."""
    G = simulation.graph or load_graph()
    source = get_nearest_node(G, from_lat, from_lng)
    target = get_nearest_node(G, to_lat, to_lng)

    results = {}
    algorithms = ["dijkstra", "astar", "bfs", "dfs", "greedy", "bellman_ford"]

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


# ─── WEBSOCKET ──────────────────────────────────────────────────


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket endpoint for real-time simulation updates."""
    await ws.accept()
    ws_clients.add(ws)
    print(f"[WS] Client connected. Total: {len(ws_clients)}")

    try:
        while True:
            # Keep connection alive; client can also send commands
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_clients.discard(ws)
        print(f"[WS] Client disconnected. Total: {len(ws_clients)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
