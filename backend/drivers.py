"""
Driver Allocation System
Manages 50 delivery drivers with nearest-driver assignment.
"""
import random
import heapq
import math
from road_network import PUNE_BOUNDS, get_nearest_node


def haversine_distance(lat1, lng1, lat2, lng2):
    """Distance in km between two points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def initialize_drivers(G, num_drivers=50):
    """
    Create driver objects at random locations in Pune.

    Each driver has:
    - id, lat, lng, status, current_node
    - active_batch, route, route_progress
    - stats (deliveries_completed, total_distance, total_time)
    """
    drivers = []
    for i in range(num_drivers):
        lat = random.uniform(PUNE_BOUNDS["south"] + 0.02, PUNE_BOUNDS["north"] - 0.02)
        lng = random.uniform(PUNE_BOUNDS["west"] + 0.02, PUNE_BOUNDS["east"] - 0.02)
        node = get_nearest_node(G, lat, lng)

        driver = {
            "driver_id": f"DRV-{i+1:03d}",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "current_node": node,
            "status": "idle",  # idle, picking, delivering, returning
            "active_batch": None,
            "route_coords": [],  # list of (lat, lng) forming the route
            "route_progress": 0,  # index into route_coords
            "current_orders": [],
            "stats": {
                "deliveries_completed": 0,
                "total_distance_m": 0,
                "total_time_s": 0,
            },
        }
        drivers.append(driver)

    return drivers


def assign_drivers_to_batches(drivers, batches, orders):
    """
    Assign idle drivers to batches using nearest-driver heuristic.
    Uses a priority queue sorted by distance.

    Returns list of (driver_index, batch_index) assignments.
    """
    idle_drivers = [(i, d) for i, d in enumerate(drivers) if d["status"] == "idle"]

    if not idle_drivers or not batches:
        return []

    assignments = []
    assigned_batches = set()
    assigned_drivers = set()

    # Build priority queue: (distance, driver_idx, batch_idx)
    heap = []
    for di, (driver_idx, driver) in enumerate(idle_drivers):
        for bi, batch in enumerate(batches):
            if batch.get("assigned", False):
                continue
            dist = haversine_distance(
                driver["lat"], driver["lng"],
                batch["centroid_lat"], batch["centroid_lng"]
            )
            
            # Smart scoring
            score = dist
            # High priority batch: artificially lower the distance cost to attract drivers
            if batch.get("is_priority", False):
                score -= 3.0  # equivalent to 3km advantage
                
            # Load balancing: slight penalty for drivers with many deliveries
            score += driver["stats"]["deliveries_completed"] * 0.1
            
            heapq.heappush(heap, (score, driver_idx, bi))

    # Greedy assignment: pick closest pairs
    while heap and len(assignments) < len(idle_drivers) and len(assignments) < len(batches):
        dist, driver_idx, batch_idx = heapq.heappop(heap)

        if driver_idx in assigned_drivers or batch_idx in assigned_batches:
            continue

        assignments.append((driver_idx, batch_idx))
        assigned_drivers.add(driver_idx)
        assigned_batches.add(batch_idx)

        # Update driver status
        drivers[driver_idx]["status"] = "picking"
        drivers[driver_idx]["active_batch"] = batches[batch_idx]["batch_id"]
        drivers[driver_idx]["current_orders"] = batches[batch_idx]["orders"]

        # Update order statuses
        for order_id in batches[batch_idx]["orders"]:
            for order in orders:
                if order["order_id"] == order_id:
                    order["status"] = "assigned"
                    order["assigned_driver"] = drivers[driver_idx]["driver_id"]
                    order["batch_id"] = batches[batch_idx]["batch_id"]
                    break

        batches[batch_idx]["assigned"] = True
        batches[batch_idx]["assigned_driver"] = drivers[driver_idx]["driver_id"]

    return assignments


def get_driver_stats(drivers):
    """Get aggregate driver statistics."""
    status_counts = {"idle": 0, "picking": 0, "delivering": 0, "returning": 0}
    total_deliveries = 0
    total_distance = 0

    for driver in drivers:
        status = driver["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        total_deliveries += driver["stats"]["deliveries_completed"]
        total_distance += driver["stats"]["total_distance_m"]

    total_drivers = len(drivers)
    active_drivers = total_drivers - status_counts.get("idle", 0)
    utilization_pct = round((active_drivers / total_drivers) * 100, 1) if total_drivers > 0 else 0

    return {
        "total_drivers": total_drivers,
        "status_breakdown": status_counts,
        "active_drivers": active_drivers,
        "utilization_pct": utilization_pct,
        "total_deliveries": total_deliveries,
        "total_distance_km": round(total_distance / 1000, 2),
    }
