"""
Order Generation System
Generates delivery orders across Pune using real restaurant data.
"""
import os
import random
import math
import uuid
from datetime import datetime, timedelta
import pandas as pd

try:
    import osmnx as ox
except ImportError:
    ox = None

from sklearn.cluster import KMeans
from road_network import PUNE_BOUNDS, get_nearest_node, DATA_DIR

RESTAURANTS_FILE = os.path.join(DATA_DIR, "restaurants.csv")
# Hotspot zone names loosely based on Pune areas
ZONE_NAMES = ["Hinjewadi", "Baner", "Kothrud", "Viman Nagar", "Wakad", "Kharadi"]


def _load_or_download_restaurants(city_name="Pune, India"):
    """Download real restaurants from OSM or load from cache."""
    clean_name = city_name.replace(", ", "_").replace(" ", "_").lower()
    rest_file = os.path.join(DATA_DIR, f"{clean_name}_restaurants.csv")

    if os.path.exists(rest_file):
        return pd.read_csv(rest_file).to_dict('records')

    if ox is None:
        raise ImportError("osmnx is required to download restaurants.")

    print(f"[SIM] Downloading real restaurant data for {city_name} from OpenStreetMap (4km radius)...")
    ox.settings.timeout = 180

    tags = {"amenity": "restaurant"}
    try:
        center = ox.geocode(city_name)
    except Exception:
        center = (18.5204, 73.8567)  # fallback

    try:
        # OSMNx 1.5+
        restaurants = ox.features_from_point(center, tags=tags, dist=4000)
    except TypeError:
        restaurants = ox.geometries_from_point(center, tags=tags, dist=4000)
    except AttributeError:
        restaurants = ox.geometries_from_point(center, tags=tags, dist=4000)

    if restaurants.empty:
        raise ValueError("No restaurants found in the specified bounding box.")

    # Convert polygons to centroids
    restaurants = restaurants.to_crs("EPSG:4326")
    centroids = restaurants.geometry.centroid

    rest_list = []
    for idx, row in restaurants.iterrows():
        name = row.get('name', 'Unknown Restaurant')
        if pd.isna(name):
            name = f"Restaurant {len(rest_list)+1}"
        
        # Get coordinates from centroid
        centroid = centroids.loc[idx]
        
        rest_list.append({
            "restaurant_id": f"R-{len(rest_list)+1:04d}",
            "name": name,
            "lat": centroid.y,
            "lng": centroid.x
        })

    df = pd.DataFrame(rest_list)

    # Compute K-Means hotspots
    print("[SIM] Clustering restaurants into hotspot zones...")
    n_clusters = min(len(ZONE_NAMES), len(df))
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    df['zone_id'] = kmeans.fit_predict(df[['lat', 'lng']])
    df['zone_name'] = df['zone_id'].apply(lambda x: ZONE_NAMES[x % len(ZONE_NAMES)])

    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(rest_file, index=False)
    print(f"[SIM] Saved {len(df)} restaurants to {rest_file}")

    return df.to_dict('records')


def _random_location_at_distance(center_lat, center_lng, min_km=2.0, max_km=4.0):
    """Generate a random location between min_km and max_km from center."""
    dist_km = random.uniform(min_km, max_km)
    angle = random.uniform(0, 2 * math.pi)

    # 1 degree lat is ~111.32 km
    # 1 degree lng is ~111.32 * cos(lat) km
    lat_offset = (dist_km * math.cos(angle)) / 111.32
    lng_offset = (dist_km * math.sin(angle)) / (111.32 * math.cos(math.radians(center_lat)))

    lat = center_lat + lat_offset
    lng = center_lng + lng_offset

    # Clamp to Pune bounds
    lat = max(PUNE_BOUNDS["south"], min(PUNE_BOUNDS["north"], lat))
    lng = max(PUNE_BOUNDS["west"], min(PUNE_BOUNDS["east"], lng))
    return lat, lng


def generate_orders(G, num_orders=1000, time_span_hours=4, city_name="Pune, India"):
    """
    Generate random delivery orders using real restaurants for the selected city.
    """
    restaurants = _load_or_download_restaurants(city_name)
    if not restaurants:
        raise ValueError(f"No restaurants available for order generation in {city_name}.")

    orders = []
    base_time = datetime.now()

    for i in range(num_orders):
        # Pick a random restaurant (real OSM data)
        rest = random.choice(restaurants)
        
        # Customer is realistic: 2 to 4 km away
        cust_lat, cust_lng = _random_location_at_distance(rest["lat"], rest["lng"], min_km=2.0, max_km=4.0)

        # Snap to graph nodes
        rest_node = get_nearest_node(G, rest["lat"], rest["lng"])
        cust_node = get_nearest_node(G, cust_lat, cust_lng)

        # Order time spread over time_span_hours
        time_offset = random.uniform(0, time_span_hours * 3600)
        order_time = base_time + timedelta(seconds=time_offset)

        order = {
            "order_id": f"ORD-{i+1:04d}",
            "restaurant_id": rest["restaurant_id"],
            "restaurant_name": rest["name"],
            "restaurant_zone": rest["zone_name"],
            "restaurant_lat": round(rest["lat"], 6),
            "restaurant_lng": round(rest["lng"], 6),
            "customer_lat": round(cust_lat, 6),
            "customer_lng": round(cust_lng, 6),
            "restaurant_node": rest_node,
            "customer_node": cust_node,
            "order_time": order_time.isoformat(),
            "status": "pending",  # pending, assigned, picked, delivered
            "assigned_driver": None,
            "batch_id": None,
            "is_priority": random.random() < 0.15, # 15% of orders are high priority
        }
        orders.append(order)

    # Sort by order time
    orders.sort(key=lambda o: o["order_time"])
    return orders


def get_order_stats(orders):
    """Get summary statistics for orders."""
    status_counts = {}
    for order in orders:
        status = order["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "total_orders": len(orders),
        "status_breakdown": status_counts,
        "pending": status_counts.get("pending", 0),
        "assigned": status_counts.get("assigned", 0),
        "picked": status_counts.get("picked", 0),
        "delivered": status_counts.get("delivered", 0),
    }
