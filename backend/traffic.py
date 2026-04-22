"""
Traffic Simulation
Dynamically assigns traffic levels to road edges.
"""
import random


# Traffic multipliers
TRAFFIC_LEVELS = {
    "low": 1.0,
    "medium": 1.3,
    "high": 1.8,
}

TRAFFIC_WEIGHTS = {
    "low": 0.5,
    "medium": 0.3,
    "high": 0.2,
}


def update_traffic(G, seed=None):
    """
    Randomly assign traffic levels to all edges.
    Updates travel_time = base_travel_time * multiplier.
    """
    if seed is not None:
        random.seed(seed)

    levels = list(TRAFFIC_LEVELS.keys())
    weights = [TRAFFIC_WEIGHTS[l] for l in levels]

    updated_count = {"low": 0, "medium": 0, "high": 0}

    for u, v, data in G.edges(data=True):
        level = random.choices(levels, weights=weights, k=1)[0]
        multiplier = TRAFFIC_LEVELS[level]
        data["traffic_level"] = level
        data["traffic_multiplier"] = multiplier
        base_time = data.get("base_travel_time", data.get("travel_time", 12))
        data["travel_time"] = base_time * multiplier
        updated_count[level] += 1

    return updated_count


def get_traffic_summary(G):
    """Get distribution of traffic levels across the network."""
    summary = {"low": 0, "medium": 0, "high": 0, "unknown": 0}
    total = 0

    for u, v, data in G.edges(data=True):
        level = data.get("traffic_level", "unknown")
        summary[level] = summary.get(level, 0) + 1
        total += 1

    if total > 0:
        summary["percentages"] = {
            k: round(v / total * 100, 1) for k, v in summary.items() if k != "percentages"
        }

    summary["total_edges"] = total
    return summary


def get_edge_traffic_level(G, u, v):
    """Get traffic level for a specific edge."""
    if G.has_edge(u, v):
        data = G.edges[u, v]
        return data.get("traffic_level", "low"), data.get("traffic_multiplier", 1.0)
    return "low", 1.0


def update_traffic_for_time(G, hour_of_day):
    """
    Update traffic based on time of day.
    Rush hours have more high-traffic roads.
    """
    morning_rush = 7 <= hour_of_day <= 10
    evening_rush = 17 <= hour_of_day <= 20
    night = hour_of_day >= 22 or hour_of_day <= 5

    if morning_rush or evening_rush:
        weights = {"low": 0.2, "medium": 0.3, "high": 0.5}
    elif night:
        weights = {"low": 0.7, "medium": 0.2, "high": 0.1}
    else:
        weights = {"low": 0.5, "medium": 0.3, "high": 0.2}

    levels = list(weights.keys())
    w = [weights[l] for l in levels]

    for u, v, data in G.edges(data=True):
        level = random.choices(levels, weights=w, k=1)[0]
        multiplier = TRAFFIC_LEVELS[level]
        data["traffic_level"] = level
        data["traffic_multiplier"] = multiplier
        base_time = data.get("base_travel_time", 12)
        data["travel_time"] = base_time * multiplier
