"""Pune Restaurant Data Module"""

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
        ]
    },
    "Hinjewadi": {
        "center": (18.5907, 73.7383),
        "restaurants": [
            {"name": "Eat India", "cuisine": "Multi-cuisine", "rating": 4.2},
            {"name": "Food Mall", "cuisine": "Food Court", "rating": 3.9},
            {"name": "Pizza King", "cuisine": "Pizza", "rating": 4.0},
            {"name": "Theobroma", "cuisine": "Bakery", "rating": 4.5},
            {"name": "Cafe 173", "cuisine": "Cafe", "rating": 4.2},
        ]
    },
    "Viman Nagar": {
        "center": (18.5679, 73.9100),
        "restaurants": [
            {"name": "Blue Lizard", "cuisine": "Pub Food", "rating": 4.2},
            {"name": "Elephant & Co", "cuisine": "Continental", "rating": 4.4},
            {"name": "Koshy", "cuisine": "South Indian", "rating": 4.0},
            {"name": "German Bakery", "cuisine": "Bakery", "rating": 4.3},
        ]
    },
    "Koregaon Park": {
        "center": (18.5362, 73.8951),
        "restaurants": [
            {"name": "The Flour Works", "cuisine": "Bakery", "rating": 4.5},
            {"name": "Sampan", "cuisine": "Chinese", "rating": 4.3},
            {"name": "Khyde", "cuisine": "Cafe", "rating": 4.4},
            {"name": "Leaping Windows", "cuisine": "Cafe", "rating": 4.2},
        ]
    },
    "Wakad": {
        "center": (18.5986, 73.7677),
        "restaurants": [
            {"name": "Mithila", "cuisine": "Maharashtrian", "rating": 4.2},
            {"name": "Vithal Roti", "cuisine": "Maharashtrian", "rating": 4.3},
            {"name": "Kokan Bhakshal", "cuisine": "Maharashtrian", "rating": 4.1},
        ]
    },
    "Hadapsar": {
        "center": (18.5089, 73.9267),
        "restaurants": [
            {"name": "Ganesh Bhel", "cuisine": "Street Food", "rating": 4.2},
            {"name": "Jagtap Dairy", "cuisine": "Dairy", "rating": 4.3},
            {"name": "Ravi Bhel", "cuisine": "Street Food", "rating": 4.1},
        ]
    },
    "Baner": {
        "center": (18.5647, 73.7719),
        "restaurants": [
            {"name": "Barbeque Nation", "cuisine": "Barbeque", "rating": 4.3},
            {"name": "Maa Lahsun", "cuisine": "North Indian", "rating": 4.1},
            {"name": "The Biryani Life", "cuisine": "Biryani", "rating": 4.4},
        ]
    }
}

TRAFFIC_ZONES = {
    "morning_rush": {"high_traffic": ["Hinjewadi", "Viman Nagar", "Wakad"], "medium_traffic": ["Kothrud", "Baner"], "low_traffic": ["Hadapsar", "Koregaon Park"]},
    "lunch_rush": {"high_traffic": ["Koregaon Park", "Kothrud", "Hadapsar"], "medium_traffic": ["Baner", "Viman Nagar"], "low_traffic": ["Hinjewadi", "Wakad"]},
    "evening_rush": {"high_traffic": ["Kothrud", "Hinjewadi", "Viman Nagar", "Wakad", "Koregaon Park"], "medium_traffic": ["Baner", "Hadapsar"], "low_traffic": []},
    "night": {"high_traffic": [], "medium_traffic": ["Viman Nagar", "Koregaon Park"], "low_traffic": ["Kothrud", "Hinjewadi", "Baner", "Wakad", "Hadapsar"]},
    "off_peak": {"high_traffic": [], "medium_traffic": ["Kothrud", "Viman Nagar"], "low_traffic": ["Hinjewadi", "Baner", "Wakad", "Hadapsar", "Koregaon Park"]}
}

def get_time_period(hour):
    if 8 <= hour < 10: return "morning_rush"
    elif 12 <= hour < 14: return "lunch_rush"
    elif 18 <= hour < 21: return "evening_rush"
    elif 22 <= hour < 24: return "night"
    return "off_peak"

def get_restaurants_by_zone(zone_name):
    return PUNE_ZONES.get(zone_name, {}).get("restaurants", [])

def get_all_restaurants():
    all_restaurants = []
    for zone_name, zone_data in PUNE_ZONES.items():
        for restaurant in zone_data["restaurants"]:
            # Copy to avoid mutating the shared PUNE_ZONES constant
            r = dict(restaurant)
            r["zone"] = zone_name
            r["center_lat"] = zone_data["center"][0]
            r["center_lng"] = zone_data["center"][1]
            all_restaurants.append(r)
    return all_restaurants

def get_traffic_level(zone_name, hour=12):
    period = get_time_period(hour)
    traffic_data = TRAFFIC_ZONES[period]
    if zone_name in traffic_data.get("high_traffic", []): return 1.8
    elif zone_name in traffic_data.get("medium_traffic", []): return 1.3
    return 0.8

def get_zone_center(zone_name):
    return PUNE_ZONES.get(zone_name, {}).get("center", (18.5204, 73.8567))
