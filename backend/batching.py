"""
Order Batching System
Clusters nearby orders using K-Means for efficient delivery.
"""
import math
import numpy as np
from sklearn.cluster import KMeans


def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def batch_orders(orders, max_per_batch=3, max_radius_km=2.0):
    """
    Cluster pending orders into batches using K-Means.

    Constraints:
    - Max 3 orders per batch
    - Orders must be within 2 km radius

    Returns list of batches, each with order indices and centroid.
    """
    pending = [o for o in orders if o["status"] == "pending"]

    if not pending:
        return []

    # Extract restaurant coordinates for clustering
    coords = np.array([
        [o["restaurant_lat"], o["restaurant_lng"]] for o in pending
    ])

    # Determine number of clusters
    n_clusters = max(1, len(pending) // max_per_batch)
    n_clusters = min(n_clusters, len(pending))

    if len(pending) <= max_per_batch:
        # All fit in one batch
        batch = {
            "batch_id": "BATCH-0001",
            "orders": [o["order_id"] for o in pending],
            "centroid_lat": float(np.mean(coords[:, 0])),
            "centroid_lng": float(np.mean(coords[:, 1])),
            "num_orders": len(pending),
            "is_priority": any(o.get("is_priority", False) for o in pending),
        }
        return [batch]

    # K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)
    centroids = kmeans.cluster_centers_

    # Group orders by cluster
    clusters = {}
    for idx, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(idx)

    batches = []
    batch_counter = 0

    for label, indices in clusters.items():
        centroid_lat = float(centroids[label][0])
        centroid_lng = float(centroids[label][1])

        # Filter by radius constraint
        valid_indices = []
        for idx in indices:
            order = pending[idx]
            dist = haversine_distance(
                order["restaurant_lat"], order["restaurant_lng"],
                centroid_lat, centroid_lng
            )
            if dist <= max_radius_km:
                valid_indices.append(idx)

        # Split into sub-batches of max_per_batch
        for i in range(0, len(valid_indices), max_per_batch):
            sub_indices = valid_indices[i:i + max_per_batch]
            batch_counter += 1

            sub_coords = coords[sub_indices]
            batch = {
                "batch_id": f"BATCH-{batch_counter:04d}",
                "orders": [pending[idx]["order_id"] for idx in sub_indices],
                "order_indices": [orders.index(pending[idx]) for idx in sub_indices],
                "centroid_lat": float(np.mean(sub_coords[:, 0])),
                "centroid_lng": float(np.mean(sub_coords[:, 1])),
                "num_orders": len(sub_indices),
                "is_priority": any(pending[idx].get("is_priority", False) for idx in sub_indices),
            }
            batches.append(batch)

    return batches
