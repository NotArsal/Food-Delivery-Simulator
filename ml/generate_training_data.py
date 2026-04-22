"""
Generate synthetic training data for delivery time prediction.
"""
import os
import sys
import random
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def generate_training_data(num_samples=10000, output_file=None):
    """
    Generate synthetic delivery data.

    Features:
    - route_distance: distance in meters (500 - 15000)
    - traffic_level: multiplier (1.0, 1.3, 1.8)
    - num_stops: number of delivery stops (1-3)
    - hour_of_day: hour (0-23)

    Target:
    - delivery_time_minutes: estimated delivery time
    """
    if output_file is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        output_file = os.path.join(DATA_DIR, "training_data.csv")

    np.random.seed(42)
    random.seed(42)

    data = []

    for _ in range(num_samples):
        # Features
        distance = np.random.uniform(500, 15000)  # meters
        traffic_level = np.random.choice([1.0, 1.3, 1.8], p=[0.5, 0.3, 0.2])
        num_stops = np.random.choice([1, 2, 3], p=[0.4, 0.4, 0.2])
        hour = np.random.randint(0, 24)

        # Calculate realistic delivery time
        # Base speed: 25 km/h in city
        base_speed_kmh = 25
        base_speed_mpm = base_speed_kmh * 1000 / 60  # meters per minute

        # Distance component
        distance_time = distance / base_speed_mpm

        # Traffic component
        traffic_factor = traffic_level

        # Stop overhead (pickup + handoff time)
        stop_time = num_stops * np.random.uniform(2, 5)  # 2-5 min per stop

        # Time-of-day factor
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            rush_factor = np.random.uniform(1.2, 1.5)
        elif 22 <= hour or hour <= 5:
            rush_factor = np.random.uniform(0.8, 1.0)
        else:
            rush_factor = np.random.uniform(1.0, 1.2)

        # Total delivery time with some noise
        delivery_time = (distance_time * traffic_factor * rush_factor + stop_time)
        noise = np.random.normal(0, delivery_time * 0.1)  # 10% noise
        delivery_time = max(3, delivery_time + noise)  # Minimum 3 minutes

        data.append({
            "route_distance": round(distance, 2),
            "traffic_level": traffic_level,
            "num_stops": num_stops,
            "hour_of_day": hour,
            "delivery_time_minutes": round(delivery_time, 2),
        })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Generated {num_samples} training samples -> {output_file}")
    print(f"\nData Summary:")
    print(df.describe())

    return df


if __name__ == "__main__":
    generate_training_data()
