"""
City-Scale Simulation Engine
Orchestrates the full delivery simulation lifecycle.
"""
import asyncio
import time
import random
import math
from datetime import datetime

from road_network import load_graph, get_node_coords
from traffic import update_traffic, get_traffic_summary
from orders import generate_orders, get_order_stats
from batching import batch_orders
from drivers import initialize_drivers, assign_drivers_to_batches, get_driver_stats
from route_optimizer import optimize_driver_route


class SimulationEngine:
    """Manages the full delivery simulation."""

    def __init__(self):
        self.graph = None
        self.orders = []
        self.drivers = []
        self.batches = []
        self.is_running = False
        self.tick_count = 0
        self.start_time = None
        self.orders_released = 0
        self.metrics = {
            "active_drivers": 0,
            "orders_pending": 0,
            "orders_delivered": 0,
            "orders_in_transit": 0,
            "avg_delivery_time_s": 0,
            "total_distance_km": 0,
            "tick": 0,
        }
        self._delivery_times = []
        self._ws_clients = set()
        self._orders_per_tick = 10  # Release 10 orders per tick
        self.tick_delay = 2.0  # Default 2 seconds
        
        # New Routing Configuration
        self.routing_mode = "dynamic" # "dynamic" or "manual"
        self.manual_algorithm = "dijkstra" # "dijkstra", "astar", "bfs", "dfs", "greedy"

    def initialize(self, num_orders=1000, num_drivers=50, city_name="Pune, India", tick_delay=2.0):
        """Load graph, generate orders and drivers."""
        print(f"[SIM] Initializing simulation for {city_name} with {num_drivers} drivers and {num_orders} orders...")
        self.graph = load_graph(city_name)
        self.tick_delay = tick_delay

        print(f"[SIM] Generating {num_orders} orders...")
        self.orders = generate_orders(self.graph, num_orders=num_orders, city_name=city_name)

        print(f"[SIM] Initializing {num_drivers} drivers...")
        self.drivers = initialize_drivers(self.graph, num_drivers=num_drivers)

        print("[SIM] Applying initial traffic conditions...")
        update_traffic(self.graph)

        self.orders_released = 0
        self.tick_count = 0
        self._delivery_times = []
        print("[SIM] Initialization complete.")

    def _release_orders(self):
        """Release a batch of orders (simulating orders coming in over time)."""
        start = self.orders_released
        end = min(start + self._orders_per_tick, len(self.orders))

        if start >= len(self.orders):
            return 0

        released = end - start
        self.orders_released = end
        return released

    def _run_batching(self):
        """Batch pending orders."""
        pending = [o for o in self.orders[:self.orders_released] if o["status"] == "pending"]
        if pending:
            self.batches = batch_orders(pending)
            return len(self.batches)
        return 0

    def _assign_drivers(self):
        """Assign idle drivers to batches."""
        unassigned = [b for b in self.batches if not b.get("assigned", False)]
        if unassigned:
            assignments = assign_drivers_to_batches(
                self.drivers, unassigned, self.orders[:self.orders_released]
            )
            return len(assignments)
        return 0

    def _compute_routes(self):
        """Compute optimized routes for newly assigned drivers."""
        for driver in self.drivers:
            if driver["status"] == "picking" and not driver["route_coords"]:
                # Find the orders for this driver
                driver_orders = []
                for order in self.orders[:self.orders_released]:
                    if order["order_id"] in driver["current_orders"]:
                        driver_orders.append(order)

                if driver_orders:
                    # Get current traffic level
                    traffic_data = get_traffic_summary(self.graph)
                    total_edges = traffic_data.get("total_edges", 0)
                    if total_edges > 0:
                        avg_traffic = (traffic_data.get("low", 0) * 1.0 + 
                                       traffic_data.get("medium", 0) * 1.3 + 
                                       traffic_data.get("high", 0) * 1.8) / total_edges
                    else:
                        avg_traffic = 1.0

                    route_coords, stops, total_dist = optimize_driver_route(
                        self.graph, driver, driver_orders,
                        routing_mode=self.routing_mode,
                        manual_algorithm=self.manual_algorithm,
                        traffic_level=avg_traffic
                    )
                    driver["route_coords"] = route_coords
                    driver["route_progress"] = 0
                    driver["total_route_distance"] = total_dist

                    # Mark orders as picked
                    for order in driver_orders:
                        order["status"] = "picked"

                    if route_coords:
                        driver["status"] = "delivering"

    def _move_drivers(self):
        """Advance drivers along their routes based on vehicle speed."""
        # 30 km/h base speed, adjusted by global traffic
        traffic_data = get_traffic_summary(self.graph)
        total_edges = traffic_data.get("total_edges", 0)
        traffic_mult = 1.0
        if total_edges > 0:
            traffic_mult = (traffic_data.get("low", 0) * 1.0 + 
                           traffic_data.get("medium", 0) * 1.3 + 
                           traffic_data.get("high", 0) * 1.8) / total_edges
        
        # Effective speed in meters per second
        speed_kmh = 40 / traffic_mult
        speed_mps = speed_kmh * 1000 / 3600
        dist_to_move = speed_mps * self.tick_delay

        for driver in self.drivers:
            if driver["status"] in ("delivering", "picking") and driver["route_coords"]:
                route = driver["route_coords"]
                progress = driver["route_progress"]
                
                if progress >= len(route) - 1:
                    self._complete_delivery(driver)
                    continue

                # Move along the coordinate list based on distance
                accumulated_dist = 0
                new_progress = progress
                
                while accumulated_dist < dist_to_move and new_progress < len(route) - 1:
                    p1 = route[new_progress]
                    p2 = route[new_progress + 1]
                    # Haversine distance between points
                    dx = (p2[0] - p1[0])
                    dy = (p2[1] - p1[1])
                    segment_dist = math.sqrt(dx ** 2 + dy ** 2) * 111000 # Approx meters
                    
                    if accumulated_dist + segment_dist > dist_to_move:
                        # Partial movement if we wanted to be extremely precise, 
                        # but advancing to the next node is enough for this simulation scale
                        break
                    
                    accumulated_dist += segment_dist
                    new_progress += 1
                
                if new_progress == progress and progress < len(route) - 1:
                    new_progress += 1 # Ensure at least 1 node progress

                driver["route_progress"] = new_progress
                new_pos = route[new_progress]
                driver["lat"] = new_pos[0]
                driver["lng"] = new_pos[1]
                driver["stats"]["total_distance_m"] += accumulated_dist

    def _complete_delivery(self, driver):
        """Mark a driver's delivery as complete."""
        # Mark orders as delivered
        for order_id in driver["current_orders"]:
            for order in self.orders:
                if order["order_id"] == order_id:
                    order["status"] = "delivered"
                    # Calculate delivery time (simulated)
                    delivery_time = random.uniform(600, 2400)  # 10-40 minutes
                    self._delivery_times.append(delivery_time)
                    break

        driver["stats"]["deliveries_completed"] += len(driver["current_orders"])
        driver["status"] = "idle"
        driver["active_batch"] = None
        driver["current_orders"] = []
        driver["route_coords"] = []
        driver["route_progress"] = 0

    def _update_metrics(self):
        """Compute current simulation metrics."""
        order_stats = get_order_stats(self.orders[:self.orders_released])
        driver_stats = get_driver_stats(self.drivers)

        avg_time = 0
        if self._delivery_times:
            avg_time = sum(self._delivery_times) / len(self._delivery_times)

        self.metrics = {
            "tick": self.tick_count,
            "active_drivers": driver_stats["active_drivers"],
            "total_drivers": driver_stats["total_drivers"],
            "orders_pending": order_stats.get("pending", 0) + order_stats.get("assigned", 0),
            "orders_in_transit": order_stats.get("picked", 0),
            "orders_delivered": order_stats.get("delivered", 0),
            "total_orders_released": self.orders_released,
            "total_orders": len(self.orders),
            "avg_delivery_time_s": round(avg_time, 1),
            "avg_delivery_time_min": round(avg_time / 60, 1),
            "total_distance_km": driver_stats["total_distance_km"],
            "driver_statuses": driver_stats["status_breakdown"],
            "utilization_pct": driver_stats.get("utilization_pct", 0),
            "simulation_speed": round(2.0 / self.tick_delay, 1) if self.tick_delay > 0 else 1
        }

    def tick(self):
        """Execute one simulation tick."""
        self.tick_count += 1

        # 1. Release new orders
        self._release_orders()

        # 2. Update traffic (every 5 ticks)
        if self.tick_count % 5 == 0:
            update_traffic(self.graph)

        # 3. Batch pending orders
        self._run_batching()

        # 4. Assign drivers
        self._assign_drivers()

        # 5. Compute routes for new assignments
        self._compute_routes()

        # 6. Move drivers
        self._move_drivers()

        # 7. Update metrics
        self._update_metrics()

    def get_state(self):
        """Get current simulation state for WebSocket broadcast."""
        driver_positions = []
        for d in self.drivers:
            driver_positions.append({
                "driver_id": d["driver_id"],
                "lat": d["lat"],
                "lng": d["lng"],
                "status": d["status"],
                "route_coords": d["route_coords"][:50] if d["route_coords"] else [],
                "progress": d["route_progress"],
                "active_batch": d["active_batch"],
                "deliveries": d["stats"]["deliveries_completed"],
            })

        # Get visible orders (restaurants & customers)
        visible_orders = []
        for o in self.orders[:self.orders_released]:
            if o["status"] != "delivered":
                visible_orders.append({
                    "order_id": o["order_id"],
                    "restaurant_lat": o["restaurant_lat"],
                    "restaurant_lng": o["restaurant_lng"],
                    "customer_lat": o["customer_lat"],
                    "customer_lng": o["customer_lng"],
                    "status": o["status"],
                })

        return {
            "tick": self.tick_count,
            "metrics": self.metrics,
            "drivers": driver_positions,
            "orders": visible_orders[:100],  # Limit for performance
            "is_running": self.is_running,
            "config": {
                "routing_mode": self.routing_mode,
                "manual_algorithm": self.manual_algorithm
            }
        }

    async def run(self, ws_broadcast_callback=None):
        """Run the simulation loop."""
        self.is_running = True
        self.start_time = time.time()
        print("[SIM] Simulation started!")

        loop = asyncio.get_running_loop()

        while self.is_running:
            try:
                # Run CPU-heavy tick in thread executor to not block the event loop
                await loop.run_in_executor(None, self.tick)

                # Broadcast state via WebSocket (now the event loop is free)
                if ws_broadcast_callback:
                    state = self.get_state()
                    await ws_broadcast_callback(state)

                if self.tick_count % 10 == 0:
                    m = self.metrics
                    print(
                        f"[SIM] Tick {m['tick']} | "
                        f"Released: {m.get('total_orders_released', 0)} | "
                        f"Pending: {m.get('orders_pending', 0)} | "
                        f"Transit: {m.get('orders_in_transit', 0)} | "
                        f"Delivered: {m.get('orders_delivered', 0)} | "
                        f"Active: {m.get('active_drivers', 0)}"
                    )

                # Check if all orders delivered
                delivered = sum(1 for o in self.orders if o["status"] == "delivered")
                if delivered >= len(self.orders):
                    print(f"[SIM] All {len(self.orders)} orders delivered!")
                    self.is_running = False
                    break

            except Exception as e:
                print(f"[SIM] Error in tick {self.tick_count}: {e}")
                import traceback
                traceback.print_exc()

            await asyncio.sleep(self.tick_delay)  # Dynamic speed

        elapsed = time.time() - self.start_time
        print(f"[SIM] Simulation completed in {elapsed:.1f}s, {self.tick_count} ticks")

    def stop(self):
        """Stop the simulation."""
        self.is_running = False
        print("[SIM] Simulation stopped.")
